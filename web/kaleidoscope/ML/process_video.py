
import os
import shutil
import cv2
from torch.utils.data import DataLoader
from moviepy.editor import VideoFileClip, ImageSequenceClip, AudioFileClip
import argparse
from options.test_options import TestOptions
from models import create_model
from data import VideoDataset
from util.util import save_image, tensor2im
import data

def get_basename_no_extension(file_path):
    base_name = os.path.basename(file_path)
    file_name_without_extension, _ = os.path.splitext(base_name)
    return file_name_without_extension

def split_video(video_path, video_folder):
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
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

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

def stylize_video(video_path, style):
    video_folder = video_path[:-4] + "_" + style
    stylized_video_path = f"{video_path[:-4]}_{style}.mp4"
    
    opt = TestOptions()
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser = opt.initialize(parser)
    opt, _ = parser.parse_known_args()
    # dataset_name = opt.dataset_mode
    # dataset_option_setter = data.get_option_setter(dataset_name)
    # parser = dataset_option_setter(parser, opt.isTrain)
    opt.num_threads = 0   # test code only supports num_threads = 0
    opt.batch_size = 1    # test code only supports batch_size = 1
    opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
    opt.display_id = -1
    opt.no_dropout = True
    opt.dataroot = video_folder
    opt.name = style 
    opt.gpu_ids = [] #TODO: Make this utilize the gpu

    original_folder, stylized_folder, sound_path, fps = split_video(video_path, video_folder)

    stylize_images(original_folder, stylized_folder, style, opt)

    sew_video(stylized_folder, sound_path, fps, stylized_video_path)

    print(f"Video Saved at {stylized_video_path}")


if __name__ == "__main__":
    style = "style_monet_pretrained"
    video_path = "/home/jwstoneb/kaleidoscope/Video_Transformation/Model/datasets/video/zoolander.mp4"
    
    stylize_video(video_path, style)
    