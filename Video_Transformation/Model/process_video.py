
import os
import shutil
import cv2
from torch.utils.data import DataLoader
from moviepy.editor import VideoFileClip, ImageSequenceClip, AudioFileClip

from options.test_options import TestOptions
from models import create_model
from data import VideoDataset

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

    # Open the video
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

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

    return original_folder, stylized_folder, audio_path


def stylize_images(original_folder, stylized_folder, style, opt):
    dataset = VideoDataset(original_folder, crop=[256, 256], resize=[286, 286])
    frame_loader = DataLoader(dataset, shuffle=False, batch_size=1)

    model = create_model(opt)
    model.setup(opt)   

    for i, data in enumerate(frame_loader):
        model.set_input(data)
        stylized_frame = model.forward(test=True)
        print(stylized_frame)





def sew_video(stylized_folder, audio_path, fps, stylized_video_path):
    """
    Create a video from a series of frames and an audio file.

    :param stylized_folde: Path to the folder containing image frames.
    :param audio_path: Path to the audio file.
    :param stylized_video_path: Path where the output video will be saved.
    :param fps: Frames per second for the video.
    """
    # Get the list of all files and directories in the specified directory
    frame_files = sorted([os.path.join(stylized_folder, f) for f in os.listdir(stylized_folder) if os.path.isfile(os.path.join(stylized_folder, f))])

    # Create a moviepy video clip from image sequence
    video_clip = ImageSequenceClip(frame_files, fps=fps)

    # Attach audio
    audio_clip = AudioFileClip(audio_path)
    video_with_audio = video_clip.set_audio(audio_clip)

    # Write the result to a file
    video_with_audio.write_videofile(stylized_video_path, codec='libx264', audio_codec='aac')

if __name__ == "__main__":
    opt = TestOptions().parse()

    style = "style_monet_pretrained"
    video_path = "/home/jwstoneb/kaleidoscope/Video_Transformation/Model/datasets/video/slap_of_god.mp4"
    video_folder = video_path[:-4] + style
    stylized_video_path = f"{video_path[:-4]}_{style}.mp4"
    opt.dataroot = video_folder

    original_folder, stylized_folder, sound_path = split_video(video_path, video_folder)
    stylize_images(original_folder, stylized_folder, style, opt)
    stylized_video_path = sew_video(stylized_folder, sound_path, stylized_video_path)

    # print(f"Video Saved at {stylized_video_path} in style of {style}")

    