
import os
import shutil
import cv2
from torch.utils.data import DataLoader
from moviepy.editor import VideoFileClip, ImageSequenceClip, AudioFileClip
import argparse
import json

from options.test_options import TestOptions
from models import create_model
from data import VideoDataset
from util.util import save_image, tensor2im
import data

def get_basename_no_extension(file_path):
    base_name = os.path.basename(file_path)
    file_name_without_extension, _ = os.path.splitext(base_name)
    return file_name_without_extension

def split_video(video_path, video_folder, opt):
    """
    Split a video into frames and save them in the specified output folder.

    :param video_path: Path to the input video.
    :param output_folder: Folder where the frames will be saved.
    """
    original_folder = os.path.join(video_folder, "original")
    stylized_folder = os.path.join(video_folder, "stylized")
    audio_path = os.path.join(video_folder, "audio.wav")

    # Create the output folder if it doesn't exist
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
        os.makedirs(original_folder)
        os.makedirs(stylized_folder)
    else:
        shutil.rmtree(video_folder)
        os.makedirs(video_folder)
        os.makedirs(original_folder)
        os.makedirs(stylized_folder)
    print("before cap")
    # Open the video
    print(video_path)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    opt.aspect_ratio = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / cap.get(cv2.CAP_PROP_FRAME_WIDTH) 

    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    print("opened")
    frame_count = 0

    while True:
        # Read a new frame
        ret, frame = cap.read()
        if not ret:
            break  # Break the loop if there are no frames left

        # Save the frame as an image file
        frame_filename = os.path.join(original_folder, f"{frame_count}.jpg")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1

    # Release the video capture object
    cap.release()
    print(f"Video split into {frame_count} frames.")

    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)

    print(video_clip.duration, audio_clip.duration)
    print(fps)
    
    return original_folder, stylized_folder, audio_path, fps


def stylize_images(original_folder, stylized_folder, style, opt):
    dataset = VideoDataset(original_folder, crop=[256, 256], resize=[286, 286])
    frame_loader = DataLoader(dataset, shuffle=False, batch_size=1) 
    N = len(dataset)

    model = create_model(opt)      # create a model given opt.model and other options
    model.setup(opt)               # regular setup: load and print networks; create schedulers

    for i, data in enumerate(frame_loader):
        frame_num = get_basename_no_extension(data['A_paths'][0])
        print(f"Style transfering frame {i}/{N}")
        model.set_input(data)
        stylized_frame = model.forward() #get the stylized frame
        stylized_frame = tensor2im(stylized_frame) #Convert Tensor to Numpy
        save_image(stylized_frame, os.path.join(stylized_folder, f"{frame_num}.png"), opt.aspect_ratio) #preprocess and save


def sew_video(stylized_folder, audio_path, fps, stylized_video_path):
    """
    Create a video from a series of frames and an audio file.

    :param stylized_folde: Path to the folder containing image frames.
    :param audio_path: Path to the audio file.
    :param stylized_video_path: Path where the output video will be saved.
    :param fps: Frames per second for the video.
    """
    # Get the list of all files and directories in the specified directory
    frame_files = [os.path.join(stylized_folder, f) for f in os.listdir(stylized_folder) if os.path.isfile(os.path.join(stylized_folder, f))]
    frame_files = sorted(frame_files, key=lambda x: int(get_basename_no_extension(x)))
    for f in frame_files:
        print(int(get_basename_no_extension(f)))


    # Create a moviepy video clip from image sequence
    video_clip = ImageSequenceClip(frame_files, fps)

    # Attach audio
    audio_clip = AudioFileClip(audio_path)
    if audio_clip.duration < video_clip.duration:
        video_clip = video_clip.subclip(0, audio_clip.duration)
    elif audio_clip.duration > video_clip.duration:
        audio_clip = audio_clip.subclip(0, video_clip.duration)
    video_with_audio = video_clip.set_audio(audio_clip)

    print(video_clip.duration, audio_clip.duration)

    # Write the result to a file
    video_with_audio.write_videofile(stylized_video_path)

def stylize_video(video_path, stylized_video_path, style):
    video_folder = video_path[:-4] + "_" + style
    
    opt = load_config("config.json")
    opt.dataroot = video_folder
    opt.name = style 

    try:
        original_folder, stylized_folder, sound_path, fps = split_video(video_path, video_folder, opt)
    except Exception:
        print(f"Error spliting video at {video_path}")
        raise Exception

    stylize_images(original_folder, stylized_folder, style, opt)

    try:
        sew_video(stylized_folder, sound_path, fps, stylized_video_path)
    except Exception:
        print(f"Error saving video at {stylized_video_path}")
        raise Exception

    shutil.rmtree(video_folder)

    print(f"Video Saved at {stylized_video_path}")


def save_arparser_json(opt, json_file_path):
    args_dict = vars(opt)

    # Save the dictionary as JSON
    json_file_path = 'args.json'  # Specify your file path here
    with open(json_file_path, 'w') as json_file:
        json.dump(args_dict, json_file, indent=4)

    print(f"Arguments saved to {json_file_path}:")
    print(json.dumps(args_dict, indent=4))

def load_config(config_path):
    # Read the JSON file into a dictionary
    with open(config_path, 'r') as json_file:
        config_dict = json.load(json_file)

    # Convert the dictionary to an argparse.Namespace object
    config = argparse.Namespace(**config_dict)

    return config

if __name__ == "__main__":
    style = "style_ukiyoe_pretrained"
    video_path = r"C:\Users\wston\Desktop\Purdue\SeniorDesign\kaleidoscope\whale.mp4"
    stylized_video_path = "stylizedtest.mp4"
    
    stylize_video(video_path, stylized_video_path, style)
    