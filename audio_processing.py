import librosa
import numpy as np
from pydub import AudioSegment
import os

class AudioProcessing:
    def __init__(self):
        self.phrase_times = []

    def detect_phrases_from_bars(self, audio_file, beats_per_bar=4):
        print(f"audio_file: {audio_file}")

        # Step 1: Load the audio file
        y, sr = librosa.load(audio_file)

        # Step 2: Detect the tempo (BPM) and beats
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        # Step 3: Convert beat frames to time in seconds
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        # Step 4: Group the beats into bars
        if len(beat_times) < beats_per_bar:
            raise ValueError("Not enough beats detected to form bars")

        bar_times = [beat_times[i] for i in range(0, len(beat_times), beats_per_bar)]

        # Calculate avg amplitude per bar
        avg_amplitudes = []
        for i in range(len(bar_times) - 1):
            start_sample = int(bar_times[i] * sr)
            end_sample = int(bar_times[i + 1] * sr)
            segment = y[start_sample:end_sample]
            avg_amplitudes.append(np.average(np.abs(segment)))

        # Ensure there are enough bars to calculate contrasts
        if len(avg_amplitudes) < 2:
            raise ValueError("Not enough bars to calculate contrasts")

        # Calculate contrast between bars as described
        contrasts = np.diff(avg_amplitudes)

        # Ensure there are contrasts to calculate
        if len(contrasts) == 0:
            raise ValueError("Not enough contrasts to detect phrase boundaries")

        # Detect phrase boundaries based on contrast
        threshold = np.percentile(contrasts, 30)
        phrase_boundaries = [i for i, contrast in enumerate(contrasts) if contrast > threshold]

        # Step 6: Apply the rule to remove consecutive bar splits
        filtered_phrase_boundaries = []
        for i in range(len(phrase_boundaries)):
            if i == 0 or phrase_boundaries[i] - phrase_boundaries[i-1] > 1:
                filtered_phrase_boundaries.append(phrase_boundaries[i])

        # Convert phrase boundaries to time
        phrase_times = [bar_times[i] for i in filtered_phrase_boundaries]
        
        self.phrase_times = phrase_times
    
    def cut_and_export_segments(self, audio_file, output_dir="segments"):
        phrase_times = self.phrase_times  # Assuming this is a class attribute
        audio = AudioSegment.from_file(audio_file)

        # Step 1: Clear the output directory
        if os.path.exists(output_dir):
            # Remove all files in the output directory
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)  # Remove the file
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
        else:
            # If the directory doesn't exist, create it
            os.makedirs(output_dir)

        # Step 2: Convert phrase times to milliseconds
        phrase_times_ms = [int(time * 1000) for time in phrase_times]

        # Step 3: Export each audio segment
        exported_files = []
        for i in range(len(phrase_times_ms) - 1):
            start_time = phrase_times_ms[i]
            end_time = phrase_times_ms[i + 1]
            segment = audio[start_time:end_time]
            output_path = os.path.join(output_dir, f"segment_{i+1}.mp3")
            segment.export(output_path, format="mp3")
            exported_files.append(output_path)
            print(f"Segment {i+1} saved as {output_path}")

        return exported_files