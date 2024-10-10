from math import e
import os
import moviepy.video.fx.all as vfx
import random
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

class VideoSynthesis:
    def combine_videos_with_audio(self, video_folder, audio_folder):
        video_files = sorted([f for f in os.listdir(video_folder) if f.endswith('.mov')])
        audio_files = sorted([f for f in os.listdir(audio_folder) if f.endswith('.mp3')])
        num_videos = len(video_files)
        num_audios = len(audio_files)
        starter = num_audios - num_videos
        # Choose a random starter from the range [1, starter + 1]
        random_starter = random.randint(1, starter + 1)
        final_clips = []
        ender = random_starter + num_videos 

        for video_file, audio_file in zip(video_files, audio_files[random_starter:ender]):
            video = VideoFileClip(os.path.join(video_folder, video_file))
            audio = AudioFileClip(os.path.join(audio_folder, audio_file))

            # Compare lengths
            video_duration = video.duration
            audio_duration = audio.duration

            if video_duration > audio_duration:
                # Trim the video symmetrically if it is longer
                trim_duration = (video_duration - audio_duration) / 2
                video = video.subclip(trim_duration, video_duration - trim_duration)
            elif audio_duration > video_duration:
                # Slow down the video to match the audio length
                speed_factor = video_duration / audio_duration
                video = video.fx(vfx.speedx, speed_factor)

            # Set audio to video
            video = video.set_audio(audio)
            final_clips.append(video)

        # Concatenate all final video clips
        final_video = concatenate_videoclips(final_clips)
        return final_video


