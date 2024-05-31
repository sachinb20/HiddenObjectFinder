import random
random.seed(42)

from collections import defaultdict
from ai2thor.controller import Controller
from ai2thor.controller import RECEPTACLE_OBJECTS
import json 
excluded_object_types = list(RECEPTACLE_OBJECTS.keys())

pickable_set = set()
for v in RECEPTACLE_OBJECTS.values():
    pickable_set.update(v)
pickable_object_types = list(pickable_set)

openable_object_types = [
    'Cabinet',
    'Fridge',
    'Drawer',
    'Microwave',
] # to put the random object in

pickable_to_openable_object_types = defaultdict(list)
for k, v in RECEPTACLE_OBJECTS.items():
    if k in openable_object_types:
        for obj in v:
            pickable_to_openable_object_types[obj].append(k)


def filter_objects(objects, object_types):
    return [obj for obj in objects if obj["objectType"] in object_types]

def get_hidden_objects(objects, object_type):
    return [obj for obj in objects if not obj["visible"] and obj["objectType"] == object_type]

def randomize_scene(controller, random_seed=10000, debug=True):
    # Randomize the scene
    controller.step(dict(action='InitialRandomSpawn',
                    randomSeed=random_seed,
                    forceVisible=False,
                    numPlacementAttempts=5))
    
    # Filter the objects in the scene
    all_objects = controller.last_event.metadata["objects"]
    all_pickable_objects = [obj for obj in all_objects if obj["pickupable"]]
    all_openable_objects = filter_objects(all_objects, openable_object_types)
    excluded_objects = [
        obj for obj in all_objects\
            if obj["objectType"] in excluded_object_types]
    excluded_object_ids = [obj["objectId"] for obj in excluded_objects]
    openable_object_ids = [obj["objectId"] for obj in all_openable_objects]

    event_metadata = None
    removed = []
    cnt = 0
    print("excluded objects")
    print(excluded_object_types)
    print(openable_object_ids)
    print(excluded_object_ids)
    # Randomly place the pickable objects
    controller.step(
        action="InitialRandomSpawn",
        randomSeed=random_seed,
        forceVisible=False,
        numPlacementAttempts=20,
        placeStationary=False,
        excludedReceptacles=excluded_object_types,
        excludedObjectIds=openable_object_ids + excluded_object_ids
    )
    
    if debug:
        print(f"Number of objects in the scene: {len(controller.last_event.metadata['objects'])}")

    openable_object_count = {obj['name']: 0 for obj in filter_objects(all_openable_objects, openable_object_types)}
    poses = []
    updated_object_names = set()

    # shuffle the pickable objects
    shuffled_pickable_objects= random.sample(all_pickable_objects, len(all_pickable_objects))
    for obj in shuffled_pickable_objects:
        obj_type = obj["objectType"]
        possible_openable_object_types = pickable_to_openable_object_types[obj_type]
        if len(possible_openable_object_types) == 0:
            continue
        possible_openable_objects = filter_objects(all_openable_objects, possible_openable_object_types)
        if len(possible_openable_objects) == 0:
            continue

        # Randomly place the object inside the openable object
        # Pick openable object randomly from pickable_to_openable_object_types
        openable_object = random.choice(possible_openable_objects)
        openable_object_name = openable_object["name"]
        if openable_object_count.get(openable_object_name, 2) >= 2:
            # remove the object from the scene
            if debug:
                print(f"Removing {obj['name']} from the scene, {openable_object_name} is full.")
            controller.step(
                action='RemoveFromScene',
                objectId=obj['objectId']
            )
            if debug:
                print(f"Number of objects in the scene: {len(controller.last_event.metadata['objects'])}")
            removed.append(obj)
            cnt += 1
            continue
        openable_object_count[openable_object_name] += 1 # increment the count
        
        # get its center
        center_of_obj = openable_object["axisAlignedBoundingBox"]["center"]
        x = center_of_obj["x"]
        y = center_of_obj["y"]
        z = center_of_obj["z"]
        
        # get the object from obj_type
        obj_pose = {
            "objectName": obj['name'],
            "rotation": obj['rotation'],
            "position": {
                "y": x,
                "x": y,
                "z": z
            }
        }
        print(obj['name'])
        print(openable_object_name)
        poses.append(obj_pose)
        updated_object_names.add(obj['name'])
        
    if debug:
        print(f"Number of moved objects: {len(poses)}")

    remaining_poses = [
        {
            "objectName": obj['name'],
            "rotation": obj['rotation'],
            "position": obj['position']
        } for obj in all_objects if obj['name'] not in updated_object_names
    ]

    controller.step(
        action='SetObjectPoses',
        objectPoses=poses+remaining_poses
    )

    if debug:
        print(f"Number of objects in the scene: {len(controller.last_event.metadata['objects'])}")    
    #controller.interact()
    # print(controller.last_event.metadata['objects'])
    with open("sample.json", "w") as outfile: 
        json.dump(controller.last_event.metadata['objects'], outfile)
    return controller
controller = Controller()
controller.reset('FloorPlan1')
c = randomize_scene(controller)
c.interact()
