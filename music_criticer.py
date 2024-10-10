from essentia.standard import MonoLoader, RhythmExtractor2013, KeyExtractor, Loudness
import openai


class MusicCriticer:
    def __init__(self, api_key):
        openai.api_key = api_key

    def analyze_music(self, mp3_file_path):
        """
        Analyze the MP3 file to extract audio features like tempo, key, and loudness using Essentia.
        """
        # Load the MP3 file and extract audio features using Essentia
        loader = MonoLoader(filename=mp3_file_path)
        audio = loader()

        # Extract rhythm (tempo)
        rhythm_extractor = RhythmExtractor2013()
        bpm, _, _, _, _ = rhythm_extractor(audio)

        # Extract key (tonality)
        key_extractor = KeyExtractor()
        key_data = key_extractor(audio)

        # Print the returned values to check what is being returned
        print("KeyExtractor returned:", key_data)

        # Extract the key and scale (only the first two values of key_data)
        key = key_data[0]  # First value is the key
        scale = key_data[1]  # Second value is the scale

        # Extract loudness
        loudness_extractor = Loudness()
        loudness = loudness_extractor(audio)

        # Return extracted features as a dictionary
        return {
            'tempo': bpm,
            'key': key,
            'scale': scale,
            'loudness': loudness
        }

        


    def judge_music(self, audio_features, video_prompt):
        """
        Use GPT-4 to judge if the extracted audio features fit the input prompt for the video.
        If not, suggest selecting another music.
        """
        # Prepare the prompt for GPT-4 based on the extracted audio features
        prompt = f"""
        The following are the extracted music features:
        - Tempo: {audio_features['tempo']} BPM
        - Key: {audio_features['key']} {audio_features['scale']}
        - Loudness: {audio_features['loudness']} dB
        
        Video description prompt: {video_prompt}
        
        Based on the audio features and the video description, determine whether this music is suitable as background music for the video. 
        ** only return "Yes" or "No". **
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an strict expert in evaluating background music suitability for video content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )

        # Extract the GPT-4 response
        decision = response.choices[0].message.content.strip()
        
        return decision

    def analyze_and_judge_music(self, mp3_file_path, video_prompt):
        """
        Analyze the music and use GPT-4 to judge whether it is suitable for the given video description.
        """
        # Step 1: Analyze the music
        audio_features = self.analyze_music(mp3_file_path)

        # Step 2: Judge if it fits the video description
        judgment = self.judge_music(audio_features, video_prompt)

        return judgment
