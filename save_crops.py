import cv2
import numpy as np
import os
import pickle


# Load all images from a folder
folder_path = '/home/dell/interaction-exploration/HiddenObjectFinder/images'
output_folder1 = '/home/dell/interaction-exploration/HiddenObjectFinder/images_ego_crops'
output_folder2 = '/home/dell/interaction-exploration/HiddenObjectFinder/images_action_crops'


if not os.path.exists(output_folder2):
    os.makedirs(output_folder2)
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
if not os.path.exists(output_folder1):
    os.makedirs(output_folder1)

Ego_grid = np.array([100,150,200,300])  # xyxy

N = 3
frame_sz = 300  # Adjust the frame size according to your image size
center = ((frame_sz // N) * (N // 2), (frame_sz // N) * ((N + 1) // 2))
actor_grid = np.array([center[0], center[0], center[1], center[1]])

file_path = 'FloorPlan1_9685294.pkl'

with open(file_path, 'rb') as f:
    data = pickle.load(f)

actions = data['action_list']
print(actions)
# Loop through all images in the folder
for i in range(len(actions)):
    for j in range(2):

        image = data['observation_list'][i][j]

        x1, y1, x2, y2 = int(Ego_grid[0]), int(Ego_grid[1]), int(Ego_grid[2]), int(Ego_grid[3])
        cropped_image1 = image[y1:y2, x1:x2]

        x1, y1, x2, y2 = int(actor_grid[0]), int(actor_grid[1]), int(actor_grid[2]), int(actor_grid[3])
        cropped_image2 = image[y1:y2, x1:x2]

        cropped_image1=cv2.cvtColor(cropped_image1, cv2.COLOR_BGR2RGB)
        output_path = os.path.join(output_folder1, f"{i}_{j}.jpg")
        cv2.imwrite(output_path, cropped_image1)
        
        # Save the cropped image
        cropped_image2=cv2.cvtColor(cropped_image2, cv2.COLOR_BGR2RGB)
        output_path = os.path.join(output_folder2, f"{i}_{j}.jpg")
        cv2.imwrite(output_path, cropped_image2)

        image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        output_path = os.path.join(folder_path, f"{i}_{actions[i]}_{j}.jpg")
        cv2.imwrite(output_path, image)

print("Images cropped and saved successfully!")





