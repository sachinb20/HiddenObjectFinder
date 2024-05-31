import pickle
import numpy as np
import cv2

def load_rgb_array_from_pkl(pkl_filename):
    with open(pkl_filename, 'rb') as file:
        data = pickle.load(file)
    return np.array(data["visualize"])

def convert_frames_to_rgb(rgb_array):
    # If the frames are in BGR format, convert them to RGB
    return np.array([cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in rgb_array])

def slow_down_frames(rgb_array, slow_timesteps, slow_factor=3):
    # Convert frames to RGB if needed (assuming input might be BGR)
    rgb_array = convert_frames_to_rgb(rgb_array)

    slowed_rgb_array = []
    for i, frame in enumerate(rgb_array):
        if i in slow_timesteps:
            slowed_rgb_array.extend([frame] * slow_factor)  # Duplicate the frame slow_factor times
        else:
            slowed_rgb_array.append(frame)
    return np.array(slowed_rgb_array)

def create_video_from_rgb_array(rgb_array, output_filename, fps=30):
    # Get the dimensions of the frames
    num_frames, height, width, _ = rgb_array.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change 'mp4v' to other codecs if needed
    video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

    for i in range(num_frames):
        # Write the frame to the video file
        frame = rgb_array[i]
        video_writer.write(frame)

    # Release the video writer object
    video_writer.release()

# Example usage:
pkl_filename = 'FloorPlan9_32423.pkl'
rgb_array = load_rgb_array_from_pkl(pkl_filename)

slow_timesteps = [
    39, 40, 88, 91, 98, 110, 118, 138, 143, 149, 186, 187, 201, 219, 232, 233, 257, 
    351, 355, 358, 359, 375, 408, 414, 454, 466, 557
] # Frames at these indices will be slowed down
slow_factor = 10  # Each specified frame will be repeated 5 times

slowed_rgb_array = slow_down_frames(rgb_array, slow_timesteps, slow_factor)
output_filename = 'output_video.mp4'
create_video_from_rgb_array(slowed_rgb_array[:600], output_filename)

