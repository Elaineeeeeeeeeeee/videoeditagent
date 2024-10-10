from openai import audio
from music_api import MusicAPI
from music_selection import MusicSelection
from audio_processing import AudioProcessing
from music_criticer import MusicCriticer
from video_synthesis import VideoSynthesis
from utils import ensure_directory_exists, export_final_video, extract_id_from_response, extract_name_from_response
import os

def main():
    music_api_key = os.getenv('MUSIC_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    # Initialize classes
    music_api = MusicAPI(music_api_key)
    audio_processing = AudioProcessing()
    video_synthesis = VideoSynthesis()

    # Ensure directories exist
    ensure_directory_exists("content/music")
    ensure_directory_exists("content/videos")
    
    # Step 1: Get instrumental music data
    music_data = music_api.search_instrumental_music()
    music_selection = MusicSelection(openai_api_key,music_data)

    # Step 2: Select music based on descriptions
    user_description = "I want the video capture the excitement and high stakes of the 2022 NBA Finals. Focus on the fast-paced action."

    clip_description = [
        "Clip 1: A highlight of a fast break with a dunk in slow motion, the crowd going wild.",
        "Clip 2: A three-point shot from Steph Curry, showing the arc of the ball as it sinks into the basket.",
        "Clip 3: Defensive plays with intense player expressions, showing a block or a steal.",
        "Clip 4: The final buzzer, with confetti falling and the players celebrating their victory."
    ]
   
   # Retry loop for selecting music and detecting phrases
    evaluated_music_ids = []  # List to keep track of already evaluated music

    while True:
        # Step 2: Select music, excluding previously evaluated ones
        selected_music = music_selection.select_music(user_description, clip_description)
        
        # Extract the current music ID
        cur_id = extract_id_from_response(selected_music)

        # Ensure that we don't select the same music again
        while cur_id in evaluated_music_ids:
            print(f"Music {cur_id} was already evaluated, selecting a new one...")
            selected_music = music_selection.select_music(user_description, clip_description)
            cur_id = extract_id_from_response(selected_music)

        print(f"Selected music: {selected_music}")

        # Step 3: Download selected music
        audio_file = music_selection.download_selected_music(selected_music, music_data, "content/music")
        print(f"Downloaded music file: {audio_file}")

        # Add the selected music ID to the list of evaluated ones
        evaluated_music_ids.append(cur_id)

        # Step 4: Use MusicCriticer to evaluate the selected music
        music_criticer = MusicCriticer(openai_api_key)

        # Analyze and judge the suitability of the music for the video
        music_features = music_criticer.analyze_music(audio_file)
        judgment = music_criticer.judge_music(music_features, clip_description)
        print(f"Judgment: {judgment}")

        # If the judgment is "yes", proceed to process the music
        if judgment.lower() == "yes":
            print(f"Music {cur_id} is suitable. Proceeding with audio processing...")
            
            try:
                # Step 5: Process audio (beat detection and segmentation)
                audio_processing.detect_phrases_from_bars(audio_file)
                audio_processing.cut_and_export_segments(audio_file)

                # If beat detection succeeds, break the loop
                print(f"Successfully detected bars and phrases for {audio_file}.")
                break  # Exit loop after successful processing

            except ValueError as e:
                # If not enough beats are detected, retry by selecting new music
                print(f"Not enough beats for {audio_file}, selecting new music and retrying...")
                continue

        else:
            # If the music is not suitable, retry
            print(f"Music {cur_id} is not suitable, retrying...")
            continue  # Loop continues to select another music


    # Step 4: Synthesize videos with music
    script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the script
    video_dir = os.path.join(script_dir, "content/videos")    # Absolute path to videos folder
    audio_dir = os.path.join(script_dir, "segments")  # Absolute path to audio segments folder
    final_video = video_synthesis.combine_videos_with_audio(video_dir, audio_dir)

    # # Export final video
    # final_video.write_videofile("content/final_output.mov", codec="libx264", audio_codec="aac")
    export_final_video(final_video)

if __name__ == "__main__":
    main()
