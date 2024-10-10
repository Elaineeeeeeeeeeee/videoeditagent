from librosa import ex
import openai
import pandas as pd
import re
from utils import extract_music_info, download_audio, extract_id_from_response, extract_name_from_response
import essentia
from essentia.standard import MonoLoader, RhythmExtractor2013, KeyExtractor, Loudness


class MusicSelection:
    def __init__(self, api_key, music_info):
        openai.api_key = api_key
        self.music_info = music_info

    def select_music(self, user_description, clip_description):
        music_info = self.music_info
        if isinstance(music_info, pd.DataFrame):
            music_info = music_info.sample(frac=1).reset_index(drop=True)
        
       
        prompt = f"""
            Based on the following video clip description and user-provided prompt, choose the best matching music from the available music data.

            User's story prompt: {user_description}
            Video clip description: {clip_description}

            Here's the available music information, including genre, speed, mood, instruments used, and the exact audio download link for each track:

            {music_info}

            Please analyze the user's story, the video clip text representation, and the music info to recommend the track that best fits the video's mood, style, and context.

            Make sure the **audiodownload** field in the output is the **full and correct download link** for the selected music, derived from the 'audiodownload' field in `music_info`. 

            Return the output **without any special characters, markdown, or extra formatting.** Use this plain text template:

            music_info:
            id: [Insert ID]
            name: [Insert Name]

            Genre: [Insert Genre]
            Speed: [Insert Speed]
            Mood: [Insert Mood]
            Instruments: [Insert Instruments]

            Reason:
            [Provide a clean and simple explanation of why the chosen music fits the video content. No extra symbols or formatting.]
            """


        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a music selection expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.2
        )

        # Return the content from the LLM assistant
        return response.choices[0].message.content.strip()
   
    def download_selected_music(self, response_text, music_data, save_dir):
        # Use regex to find the music id from the response_text
        music_id = extract_id_from_response(response_text)
        music_name = extract_name_from_response(response_text)

        if music_id is not None and music_name is not None: 

            print(f"Music ID extracted: {music_id}")
            print(f"Music name extracted: {music_name}")

            # Retrieve the correct audio download link using the music_id
            matching_music = music_data[music_data['id'] == music_id]

            # Check if there is a match in the DataFrame
            if not matching_music.empty:
                music_url = matching_music['audiodownload'].values[0]
                return download_audio(music_url, save_dir, music_name)
            else:
                raise ValueError(f"No matching music found for ID: {music_id}")
        else:
            raise ValueError("No music ID found in the response.")
