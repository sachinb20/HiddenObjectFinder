import random
random.seed(42)

from ai2thor.controller import Controller

excluded_object_types = [] # to keep static and avoid placing random objects on them

pickable_object_types = [
    'Apple',
    'Bowl',
    'Egg',
    'Bottle',
    'Bread',
    'ButterKnife',
    'Cup',
    'Mug',
    'Tomato',    
    'PepperShaker'
] # to randomize

openable_object_types = [
    'Cabinet',
    'Fridge',
    'Drawer'
] # to put the random object in

pickable_to_openable_object_types = {
    'Apple': ['Fridge'],
    'Bowl': ['Drawer', 'Cabinet'],
    'Egg': ['Fridge'],
    'Bottle': ['Cabinet'],
    'Bread': ['Fridge'],
    'ButterKnife': ['Drawer'],
    'Cup': ['Drawer', 'Cabinet'],
    'Mug': ['Drawer', 'Cabinet'],
    'Tomato': ['Fridge'],
    'PepperShaker': ['Drawer']
}

def randomize_scene(scene_name, random_seed=42, debug=False):
    # Create an AI2-THOR controller
    controller = Controller()

    # Set the scene to the specified scene name
    event = controller.reset(scene_name)
    
    # Filter the objects in the scene
    objects = controller.last_event.metadata["objects"]
    pickable_objects = filter_objects(objects, pickable_object_types)
    openable_objects = filter_objects(objects, openable_object_types)
    excluded_objects = [
        obj for obj in objects\
            if obj["objectType"] not in pickable_object_types + openable_object_types]
    excluded_object_types = [obj["objectType"] for obj in excluded_objects]
    excluded_object_ids = [obj["objectId"] for obj in excluded_objects]
    openable_object_ids = [obj["objectId"] for obj in openable_objects]
    
    # Ramdomly pick an object to randomize
    random_object = random.choice(pickable_objects)
    random_object = filter_objects(objects, ['Apple'])[0]

    event_metadata = None
    cnt = 0
    # Randomize the scene
    while cnt < 5:
        # Randomly place the object
        controller.step(
            action="InitialRandomSpawn",
            randomSeed=random_seed,
            forceVisible=False,
            numPlacementAttempts=20,
            placeStationary=False,
            numDuplicatesOfType = [
                {
                    "objectType": random_object['objectType'],
                    "count": 2
                },
            ],
            excludedReceptacles=excluded_object_types,
            excludedObjectIds=openable_object_ids + excluded_object_ids
        )
        
        # Check if the object is hidden
        hidden_objects = get_hidden_objects(
            controller.last_event.metadata["objects"], 
            random_object['objectType'])
        if len(hidden_objects) > 0:
            event_metadata = controller.last_event.metadata
            # Remove the all objects of random object type, except the hidden object
            hidden_object = hidden_objects[-1]
            # objects_of_random_object_type = filter_objects(objects, [random_object['objectType']])
            objects_of_random_object_type = filter_objects(event_metadata["objects"], [random_object['objectType']])

            if debug:
                print(f"Hidden object: {hidden_object['objectId']}")
            # for obj in hidden_objects:
            for obj in objects_of_random_object_type:
                if obj["objectId"] != hidden_object["objectId"]:
                    event_metadata = controller.step(
                        action="RemoveFromScene", 
                        objectId=obj["objectId"]
                    ).metadata
                    if debug:
                        objid = obj["objectId"]
                        print(f"Removed {objid}")
            
            # place the random object in the openable object
            hidden_obj_name = hidden_object['name']
            openable_object_type = pickable_to_openable_object_types[random_object['objectType']]
            openable_object = random.choice(filter_objects(openable_objects, openable_object_type))

            # get its center
            center_of_obj = openable_object["axisAlignedBoundingBox"]["center"]
            x = center_of_obj["x"]
            y = center_of_obj["y"]
            z = center_of_obj["z"]
            
            if debug:
                print(f"Openable object: {openable_object['objectId']}")
                print(f"Center of object: {center_of_obj}")
                print(f'Previous position: {hidden_object["position"]}')
                print(f"Placing {hidden_obj_name} at ({x}, {y}, {z})")
                
            hidden_obj_pose = {
                "objectName": hidden_obj_name,
                "rotation": hidden_object['rotation'],
                "position": {
                    "y": x,
                    "x": y,
                    "z": z
                }
            },
            
            # keep the remaining objects at same place and position
            remaining_obj_poses = [
                {
                    "objectName": obj["name"],
                    "rotation": obj['rotation'],
                    "position": obj['position']
                } for obj in pickable_objects if obj["objectId"] != hidden_object["objectId"]
            ]
            
            event_metadata = controller.step(
                action='SetObjectPoses',
                objectPoses=[
                    hidden_obj_pose,
                ] + remaining_obj_poses
            ).metadata


            break
        cnt += 1

    # Stop the controller
    controller.stop()

    # Return the scene
    return event.metadata, event_metadata, random_object, hidden_object

def filter_objects(objects, object_types):
    return [obj for obj in objects if obj["objectType"] in object_types]

def get_hidden_objects(objects, object_type):
    return [obj for obj in objects if not obj["visible"] and obj["objectType"] == object_type]
