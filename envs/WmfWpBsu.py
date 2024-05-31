from ai2thor.controller import Controller, RECEPTACLE_OBJECTS

seed = 42
base_scene_name = 'FloorPlan'
ids = [1, 2, 3, 4, 5]
openable_object_types = [
    "Fridge",
    "Cabinet",
    "Microwave",
    "Drawer"
]

openable_to_pickable_object_types = {
    # 'Fridge': ['Apple', 'Egg', 'Tomato', 'Bread'],
    'Fridge': RECEPTACLE_OBJECTS['Fridge'],
    # 'Microwave': ['Bowl', 'Mug'],
    'Microwave': RECEPTACLE_OBJECTS['Microwave'],
    # 'Cabinet': ['Bowl', 'Cup', 'Mug', 'Bottle'],
    'Cabinet': RECEPTACLE_OBJECTS['Cabinet'],
    'Drawer': ['Knife', 'ButterKnife', 'PepperShaker']
}

def get_scene_name(base_scene_name, scene_id):
    return f"{base_scene_name}{scene_id}"

def put_obj_manually(obj, receptacle_obj, controller):
    controller.step(
        action="PickupObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    
    if not controller.last_event.metadata['lastActionSuccess']:
        return False

    controller.step(dict(action='OpenObject', 
                         objectId=receptacle_obj['objectId'], 
                         forceAction=True))
    
    if not controller.last_event.metadata['lastActionSuccess']:
        return False

    controller.step(dict(action='PutObject',
                        objectId = receptacle_obj['objectId'],
                        forceAction = True))
    
    if not controller.last_event.metadata['lastActionSuccess']:
        return False

    controller.step(dict(action='CloseObject', 
                         objectId=receptacle_obj['objectId'], 
                         forceAction=True))
    
    return controller.last_event.metadata['lastActionSuccess']
    
def randomize_scene(scene_id=1, random_seed=42, debug=False):
    controller = Controller()
    scene_name = get_scene_name(base_scene_name, scene_id)
    controller.reset(scene_name)

    # Randomize the scene
    objects = controller.last_event.metadata['objects']
    receptacles= [obj["objectType"] for obj in objects if obj["receptacle"]]
    receptacles = list(set(receptacles))
    controller.step(dict(action='InitialRandomSpawn',
                    randomSeed=random_seed,
                    forceVisible=False,
                    numPlacementAttempts=5,
                    placeStationary=False,
                    excludedReceptacles=receptacles))
    
    # Manually place the objects for each openable object
    used_objects = set()
    for openable_obj in openable_object_types:
        flag = False
        pickable_objects = openable_to_pickable_object_types[openable_obj]
        receptacle_objs = [obj for obj in objects if obj['objectType'] == openable_obj]
        if len(receptacle_objs) == 0:
            if debug:
                print(f"No {openable_obj} in the scene")
            continue
        receptacle_obj = receptacle_objs[0]
        for pickable_obj in pickable_objects:
            for obj in objects:
                if obj['objectType'] != pickable_obj or obj['objectId'] in used_objects:
                    continue
                retval = put_obj_manually(obj, receptacle_obj, controller)
                if retval:
                    used_objects.add(obj['objectId'])
                    if debug:
                        print(f"Successfully placed {pickable_obj} in {openable_obj}")
                    flag = True
                    break
            if flag:
                break
        if debug and not flag:
            print(f"Failed to place an object in {openable_obj}")
 
    return controller

if __name__ == "__main__":
    c = randomize_scene(5, seed, debug=True)
    c.interact()
