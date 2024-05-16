import cv2
import numpy as np
import os

# Load all images from a folder
folder_path = '/home/dell/interaction-exploration/HiddenObjectFinder/sample_images'
output_folder1 = '/home/dell/interaction-exploration/HiddenObjectFinder/sample_images_bbox'
output_folder2 = '/home/dell/interaction-exploration/HiddenObjectFinder/sample_images_bbox4pick'
image_files = os.listdir(folder_path)

# Define bounding box coordinates
N = 3
frame_sz = 300  # Adjust the frame size according to your image size
center = ((frame_sz // N) * (N // 2), (frame_sz // N) * ((N + 1) // 2))

center_grid = np.array([[center[0], center[0], center[1], center[1]]])  # xyxy
print(center_grid)
# Create output folder if it doesn't exist
if not os.path.exists(output_folder1):
    os.makedirs(output_folder1)

# Loop through all images in the folder
for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)
    image = cv2.imread(image_path)

    # Draw bounding box on the image
    for box in center_grid:
        pt1 = (int(box[0]), int(box[1]))
        pt2 = (int(box[2]), int(box[3]))
        print(pt1,pt2)
        cv2.rectangle(image, pt1, pt2, (0, 255, 0), 2)  # Green color, thickness = 2

    # Save the modified image
    output_path = os.path.join(output_folder1, image_file)
    cv2.imwrite(output_path, image)

print("Bounding boxes added and images saved successfully!")

center_grid = np.array([[100,300,200,150]])  # xyxy
print(center_grid)
# Create output folder if it doesn't exist
if not os.path.exists(output_folder2):
    os.makedirs(output_folder2)

# Loop through all images in the folder
for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)
    image = cv2.imread(image_path)

    # Draw bounding box on the image
    for box in center_grid:
        pt1 = (int(box[0]), int(box[1]))
        pt2 = (int(box[2]), int(box[3]))
        print(pt1,pt2)
        cv2.rectangle(image, pt1, pt2, (0, 255, 0), 2)  # Green color, thickness = 2

    # Save the modified image
    output_path = os.path.join(output_folder2, image_file)
    cv2.imwrite(output_path, image)

print("Bounding boxes added and images saved successfully!")

