import os
import pickle

# Directory containing the PKL files
directory = 'ObjCov_rollouts'

# Initialize dictionaries to store lengths
floorplan_pick_lengths = {1: [], 3: [], 4: [], 5: [], 9: []}
floorplan_cov_lengths = {1: [], 3: [], 4: [], 5: [], 9: []}

# Iterate over each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.pkl'):
        # Determine the floor plan type
        for fp_type in [1, 3, 4, 5, 9]:
            if f'FloorPlan{fp_type}_' in filename:
                # Load the PKL file
                with open(os.path.join(directory, filename), 'rb') as file:
                    # print(file)
                    data = pickle.load(file)
                    # Extract lengths
                    picked_up = []

                    for i in range(len(data['metadata_list'])):
                        for j in range(2):
                            metadata = data['metadata_list'][i][j]
                            # print(i)
                            if metadata is not None:
                                for obj in metadata["objects"]:
                                    if obj["isPickedUp"]:
                                        picked_up.append(obj["objectId"])

                    pick_length = len(list(set(picked_up)))
                    # pick_length = len(data['obj_pick_step'])
                    cov_length = len(data['obj_cov_step'])
                    # Store lengths in the corresponding list
                    floorplan_pick_lengths[fp_type].append(pick_length)
                    floorplan_cov_lengths[fp_type].append(cov_length)
                break

# Print the results
for fp_type in [1, 3, 4, 5, 9]:
    print(f"FloorPlan{fp_type} - Pick lengths: {floorplan_pick_lengths[fp_type]}")
    print(f"FloorPlan{fp_type} - Cov lengths: {floorplan_cov_lengths[fp_type]}")

Floor4 =['Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Fridge', 'Microwave']
Floor9= ['Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Fridge', 'Microwave']
Floor2= ['Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Microwave', 'Fridge']
Floor3 =['Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Fridge', 'Microwave', 'Drawer', 'Drawer', 'Drawer', 'Drawer', 'Drawer', 'Drawer']
Floor5 = ['Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Cabinet', 'Cabinet', 'Drawer', 'Cabinet', 'Microwave', 'Fridge']
Floor1 = ['Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Microwave', 'Fridge']

print(len(Floor1))
# print(len(Floor2))
print(len(Floor3))
print(len(Floor4))
print(len(Floor5))
print(len(Floor9))

# import os
# import pickle
# import matplotlib.pyplot as plt
# import numpy as np

# # Directory containing the PKL files
# directory = 'ObjCov_rollouts'

# # Initialize dictionaries to store lengths
# floorplan_pick_lengths = {1: [], 2: [], 3: [], 4: [], 5: [], 9: []}
# floorplan_cov_lengths = {1: [], 2: [], 3: [], 4: [], 5: [], 9: []}

# # Predefined values
# max_len = 100  # Example max_len value
# initialized_beforehand = 50  # Example initialized_beforehand value

# # Iterate over each file in the directory
# for filename in os.listdir(directory):
#     if filename.endswith('.pkl'):
#         # Determine the floor plan type
#         for fp_type in [1, 2, 3, 4, 5, 9]:
#             if f'FloorPlan{fp_type}_' in filename:
#                 # Load the PKL file
#                 with open(os.path.join(directory, filename), 'rb') as file:
#                     data = pickle.load(file)
#                     # Extract lengths
#                     pick_length = len(data['obj_pick_step'])
#                     cov_length = len(data['obj_cov_step'])
#                     # Store lengths in the corresponding list
#                     floorplan_pick_lengths[fp_type].append(pick_length)
#                     floorplan_cov_lengths[fp_type].append(cov_length)
#                 break

# # Generate charts
# for fp_type in [1, 2, 3, 4, 5, 9]:
#     if floorplan_cov_lengths[fp_type]:  # Ensure there is data to plot
#         fig, ax = plt.subplots()
#         x = np.arange(len(floorplan_cov_lengths[fp_type]))  # the label locations
#         width = 0.2  # the width of the bars

#         # Data for the bars
#         max_len_data = [max_len] * len(floorplan_cov_lengths[fp_type])
#         initialized_beforehand_data = [initialized_beforehand] * len(floorplan_cov_lengths[fp_type])
#         obj_cov_step_data = floorplan_cov_lengths[fp_type]

#         # Plotting the bars
#         rects1 = ax.bar(x - width, max_len_data, width, label='Max Len')
#         rects2 = ax.bar(x, initialized_beforehand_data, width, label='Initialized Beforehand')
#         rects3 = ax.bar(x + width, obj_cov_step_data, width, label='Object Coverage Step')

#         # Add some text for labels, title, and custom x-axis tick labels, etc.
#         ax.set_xlabel('File Index')
#         ax.set_ylabel('Coverage')
#         ax.set_title(f'Coverage for FloorPlan{fp_type}')
#         ax.set_xticks(x)
#         ax.legend()

#         fig.tight_layout()
#         plt.show()
