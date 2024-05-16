from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
import json
import math
from typing import Dict, List
import numpy as np
import random
def create_scene_graph(objects):
    scene_graph = {}
    scene_graph["Agent"]={  
            "position": {
      "x": -0.34021228551864624,
      "y": 0.9094499349594116,
      "z": 1.0938019752502441
    },
        "center": {
      "x": -0.34021228551864624,
      "y": 0.9094499349594116,
      "z": 1.0938019752502441
    },

            "BoundingBox": [
      [
        -2.0334811210632324,
        1.7936310768127441,
        -0.2726714611053467
      ],
      [
        -2.0334811210632324,
        1.7936310768127441,
        -1.2774642705917358
      ],
      [
        -2.0334811210632324,
        -0.008308768272399902,
        -0.2726714611053467
      ],
      [
        -2.0334811210632324,
        -0.008308768272399902,
        -1.2774642705917358
      ],
      [
        -2.7560410499572754,
        1.7936310768127441,
        -0.2726714611053467
      ],
      [
        -2.7560410499572754,
        1.7936310768127441,
        -1.2774642705917358
      ],
      [
        -2.7560410499572754,
        -0.008308768272399902,
        -0.2726714611053467
      ],
      [
        -2.7560410499572754,
        -0.008308768272399902,
        -1.2774642705917358
      ]
    ],
            "parentReceptacles": ["Floor|+00.00|+00.00|+00.00"],
            "ObjectState": None
            }
    

    OBJECT_LIST = []
    for obj in objects:
        obj_id = obj["objectId"]
        aabb = obj["objectOrientedBoundingBox"]["cornerPoints"] if obj["pickupable"] else obj["axisAlignedBoundingBox"]["cornerPoints"]

        if obj["openable"]:
            if obj["isOpen"]:
                object_state = "Open"
            else:
                object_state = "Closed"
        else:
            object_state = None
        
        scene_graph[obj_id] = {
            "position": obj["position"],
            "center": obj["axisAlignedBoundingBox"]["center"],
            "BoundingBox": aabb,
            "parentReceptacles": obj["parentReceptacles"],
            "ObjectState": object_state
        }
        OBJECT_LIST.append(obj["objectType"])

    return scene_graph, OBJECT_LIST

def find_keys(input_key, data):
    input_key = input_key.lower()
    matching_keys = []
    for key in data.keys():
        if key.lower().startswith(input_key):
            matching_keys.append(key)
    return matching_keys

def calculate_object_center(bounding_box):
    x_coords = [point[0] for point in bounding_box]
    y_coords = [point[1] for point in bounding_box]
    z_coords = [point[2] for point in bounding_box]
    center = {
        'x': sum(x_coords) / len(bounding_box),
        'y': sum(y_coords) / len(bounding_box),
        'z': sum(z_coords) / len(bounding_box)
    }
    return center

def closest_position(
    object_position: Dict[str, float],
    reachable_positions: List[Dict[str, float]]
) -> Dict[str, float]:
    out = reachable_positions[0]
    min_distance = float('inf')
    for pos in reachable_positions:
        # NOTE: y is the vertical direction, so only care about the x/z ground positions
        dist = sum([(pos[key] - object_position[key]) ** 2 for key in ["x", "z"]])
        if dist < min_distance:
            min_distance = dist
            out = pos
    return out


def get_angle_and_closest_position(controller, object_type, scene_graph):
    # Extracting object and agent positions
    # types_in_scene = sorted([obj["objectType"] for obj in controller.last_event.metadata["objects"]])
    # assert object_type in types_in_scene
    # # print(types_in_scene)
    # obj = next(obj for obj in controller.last_event.metadata["objects"] if obj["objectType"] == object_type)

    keys = find_keys(object_type, scene_graph)
    object_id = keys[0]                       #Choose first key
    obj_position = calculate_object_center(scene_graph[object_id]['BoundingBox'])

    # Save the reachable positions of the scene to a file
    reachable_positions = controller.step(
        action="GetReachablePositions", raise_for_failure=True
    ).metadata["actionReturn"]

    
    closest = closest_position(obj_position, reachable_positions)

    target_obj = controller.last_event.metadata["objects"][0]
    obj_x = target_obj["position"]["x"]
    obj_z = target_obj["position"]["z"]

    agent_position = controller.last_event.metadata["agent"]["position"]
    agent_x = agent_position["x"]
    agent_z = agent_position["z"]

    delta_x = obj_x - agent_x
    delta_z = obj_z - agent_z
    angle_rad = math.atan2(delta_z, delta_x)

    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg, closest, object_id

def euclidean_distance(pos1, pos2):
    # print(pos1)
    # print(pos2)
    return math.sqrt((pos1['x'] - pos2['x'])**2 + (pos1['y'] - pos2['y'])**2 + (pos1['z'] - pos2['z'])**2)


def find_closest_items(agent_position, scene_graph, num_items=5):
    distances = {}
    for obj_id, obj_data in scene_graph.items():
        # obj_position = obj_data['position']
        obj_aabb = obj_data['BoundingBox']
        obj_center = calculate_object_center(obj_aabb)
        # Adjusting object position relative to the agent
        obj_position_global = {
            'x': obj_center['x'] ,
            'y': obj_center['y'] ,
            'z': obj_center['z'] 
        }
        # Calculate distance from agent to object
        distance = euclidean_distance(agent_position, obj_position_global)
        distances[obj_id] = distance
    # Sort distances and return the closest items
    closest_items = sorted(distances.items(), key=lambda x: x[1])[:num_items]
    return closest_items

import cv2

def save_frame(controller,state):

    bgr_frame = cv2.cvtColor(controller.last_event.frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(state+'.jpg', bgr_frame)

    return bgr_frame

def visible_state(controller,target_receptacle):
    visibility_states = []

    for angle in range(12):
        last_rot = controller.last_event.metadata["agent"]["rotation"]["y"]
        controller.step(
            action="RotateLeft",
            degrees=30
        )
        #In case agent is stuck while rotating
        if last_rot == controller.last_event.metadata["agent"]["rotation"]["y"]:
            print("mera yasu yasu")
            rewind_angle = 1*30
            return rewind_angle
        

        types_in_scene = sorted([obj["objectType"] for obj in controller.last_event.metadata["objects"]])
        assert target_receptacle in types_in_scene
        # print(types_in_scene)
        obj = next(obj for obj in controller.last_event.metadata["objects"] if obj["objectType"] == target_receptacle)
        print(obj['visible'])
        visibility_states.append(obj['visible'])

        save_frame(controller,target_receptacle+'/'+str(angle+30))
 
    print(visibility_states)

    return visibility_states

def perturb(controller):
    # Define a list of actions
    actions = ["MoveAhead", "MoveBack", "MoveLeft", "MoveRight"]
    
    # Choose a random action
    action = random.choice(actions)
    
    # Execute the chosen action
    controller.step(action)
    return None

def shift_indices(arr):
    continuous_parts = []
    current_part = [arr[0]]

    for i in range(1, len(arr)):
        if arr[i] == arr[i-1] + 1:
            current_part.append(arr[i])
        else:
            continuous_parts.append(current_part)
            current_part = [arr[i]]

    print(current_part)
    print(continuous_parts)
    if continuous_parts == []:
      return current_part
    else:
      return np.concatenate((current_part, continuous_parts[0]))
    

def rotate_angle(controller,target_receptacle):


    # # Find the indices of all True values in the cyclical array
    # true_indices = [i for i, val in enumerate(visibility_states) if val]

    # # Calculate the total number of True values
    # num_true = len(true_indices)

    # # Calculate the length of the array
    # array_length = len(visibility_states)

    # # Initialize the shifted array
    # shifted_visibility_states = [False] * array_length

    # # Shift the segments if necessary
    # if num_true > 0:
    #     first_true_index = true_indices[0]
    #     shift_amount = array_length - first_true_index
    #     for i, val in enumerate(visibility_states):
    #         if val:
    #             shifted_visibility_states[(i + shift_amount) % array_length] = True

    visibility_states = visible_state(controller,target_receptacle)

    #Not well written but returns 30 degree rewind incase of hitting obs during rotation
    if type(visibility_states)  == int:
        return visibility_states
    
    #check whether not visible then pertube the agent
    while all(not elem for elem in visibility_states):
        perturb(controller)
        visibility_states = visible_state(controller,target_receptacle)


    true_indices = [i for i, val in enumerate(visibility_states) if val]

    # Find the indices of all True values in the shifted array
    shifted_true_indices = shift_indices(true_indices)
    midpoint_index = (len(shifted_true_indices) - 1) // 2

    # Get the index of the middle True value
    middle_index = shifted_true_indices[midpoint_index]
    print(middle_index)
    # Calculate the angle needed to rewind the rotation to that position
    rewind_angle = (11-middle_index) * 30

    return rewind_angle


def update_scene_graph(scene_graph,action,obj_id,recept_id):

    if action == "Pickup":
        scene_graph[obj_id]['parentReceptacles'] = ["Agent"]

    elif action == "Putdown":
        scene_graph[obj_id]['parentReceptacles'] = [recept_id]

    elif action == "Open":
        scene_graph[obj_id]['ObjectState'] = "Open"

    elif action == "Close":
        scene_graph[obj_id]['ObjectState'] = "Close"

    elif action == "Navigate":
        scene_graph = scene_graph

    return scene_graph


controller = Controller(
	agentMode = "arm",
    gridSize=0.5,
    rotateStepDegrees=2,
    snapToGrid=False,
    # scene=get_scene(args.scene_name),
    scene="FloorPlan18",
    # camera properties
    width=640,
    height=480,
    fieldOfView=90,
)

# controller.step(
#     action="LookUp",
#     degrees=30
# )

# agent_logs = controller.interact()


 #Create OG SG
controller.step("MoveBack")
event = controller.step("MoveAhead")
print(event.metadata["objects"])
scene_graph, object_list = create_scene_graph(event.metadata["objects"])

# Save scene graph to a file
# file_path = "scene_graph.json"
# with open(file_path, "w") as json_file:
#     json.dump(scene_graph, json_file, indent=2)

# print(f"Scene graph saved to {file_path}")

target_receptacle = "Cabinet"
source_receptacle = "None"
object = "Mug"

###############################################################################################
#Navigate + Tune Location (To View Object + Effective Manip)
angle_deg, closest, target_recept_id = get_angle_and_closest_position(controller,target_receptacle,scene_graph)
print(closest)
event = controller.step(action="Teleport", **closest)
print(event.metadata["agent"]["position"])  
angle = rotate_angle(controller, target_receptacle)
# # Rewind the rotation
controller.step(
    action="RotateRight",  # Rewind the rotation by rotating right
    degrees=angle
)

event = controller.step("MoveBack")

save_frame(controller,"1")

# #TargetReceptacle Manipulation (Open)
controller.step(
    action="OpenObject",
    objectId=target_recept_id,
    openness=1,
    forceAction=False
)

save_frame(controller,"2")

#Verify Action + Update SG

# #Update SG
action = "Open"
scene_graph = update_scene_graph(scene_graph,action,target_recept_id,None)


##########################################################################################
#
#SourceReceptaple Manipulation (Open)
#
########################################################################################3

#Navigate to Object
angle_deg, closest, obj_id = get_angle_and_closest_position(controller,object,scene_graph)

controller.step(action="Teleport", **closest)

save_frame(controller,"test1")
closest_items = find_closest_items(event.metadata["agent"]["position"], scene_graph, num_items=5)
angle = rotate_angle(controller, object)
controller.step(
    action="RotateRight",
    degrees=angle
)

controller.step(
    action="OpenObject",
    objectId=target_recept_id,
    openness=1,
    forceAction=True
)

bgr_frame = save_frame(controller,"3")
# caption, text_prompt = tagging_module(bgr_frame)

#Verify
# print(text_prompt)
# print(closest_items)

#Object Pickup
event = controller.step(
action="PickupObject",
objectId=obj_id,
forceAction=False,
manualInteract=False
)

bgr_frame = save_frame(controller,"4")
# black_image = get_mask_with_pointprompt(bgr_frame)
# frame = cv2.cvtColor(black_image,cv2.COLOR_RGB2BGR)


#Verify 
# caption, text_prompt = tagging_module(frame)
# print(caption)
# print(text_prompt)

#Update SG
action = "Pickup"
scene_graph = update_scene_graph(scene_graph,action,obj_id,None)
print(scene_graph[obj_id])

print(event.metadata["agent"]["position"])



############################################################################
#Receptacle Navigation

angle_deg, closest, recept_id = get_angle_and_closest_position(controller,target_receptacle,scene_graph)
print(closest)
event = controller.step(action="Teleport", **closest)
print(event.metadata["agent"]["position"])
# event = controller.step("MoveBack")
# event = controller.step("MoveRight")
save_frame(controller,"test1")

angle = rotate_angle(controller, target_receptacle)
# Rewind the rotation
print(angle)
controller.step(
    action="RotateRight",  # Rewind the rotation by rotating right
    degrees=angle
)
save_frame(controller,"test2")
# event = controller.step("MoveBack")

save_frame(controller,"5")
# controller.step("MoveBack")
print(recept_id)
#Object Putdown
controller.step(
action="PutObject",
objectId=recept_id,
forceAction=False,
placeStationary=True
)

save_frame(controller,"6")


#Verify
action = "Putdown"
scene_graph = update_scene_graph(scene_graph,action,obj_id,recept_id)    
print(scene_graph[obj_id])
###########################################################################3
#
#TargetReceptacle Manipulation (Close)

controller.step(
action="CloseObject",
objectId=recept_id,
forceAction=False
)

save_frame(controller,"7")

# #Verify

# #Update SG
action = "Close"
scene_graph = update_scene_graph(scene_graph,action,recept_id,None)
