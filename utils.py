import os
import re
import requests

# Utility function to download and save audio files from a URL
def download_audio(url, save_dir, file_name):
    response = requests.get(url)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, f"{file_name}.mp3")
    with open(file_path, 'wb') as f:
        f.write(response.content)
    print(f"Audio saved at {file_path}")
    return file_path

# Utility function to extract URLs and music names from LLM response
def extract_music_info(response_text):
    url_pattern = r'https?://[^\s]+'
    name_pattern = r'name: (.*?)\n'

    url_match = re.search(url_pattern, response_text)
    name_match = re.search(name_pattern, response_text)

    music_url = url_match.group(0) if url_match else None
    music_name = name_match.group(1).strip() if name_match else None

    return music_name, music_url

# Utility function to list files in a directory
def list_files_in_directory(directory, extension=None):
    files = [f for f in os.listdir(directory) if not extension or f.endswith(extension)]
    files.sort()
    return files

# Utility function to ensure required directories exist
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_unique_filename(output_dir, base_filename, extension=".mov"):
    """
    Generate a unique filename by appending a number if the file already exists.
    
    Args:
        output_dir (str): The directory where the file will be saved.
        base_filename (str): The base name of the file.
        extension (str): The file extension (e.g., ".mov").
    
    Returns:
        str: A unique filename.
    """
    filename = f"{base_filename}{extension}"
    counter = 1
    # Loop until a unique filename is found
    while os.path.exists(os.path.join(output_dir, filename)):
        filename = f"{base_filename}_{counter}{extension}"
        counter += 1
    return os.path.join(output_dir, filename)

def export_final_video(final_video, output_dir="content", base_filename="final_output", extension=".mov"):
    """
    Export the final video, ensuring that no file is overwritten.
    """
    unique_filename = get_unique_filename(output_dir, base_filename, extension)
    
    # Now write the final video file to disk
    final_video.write_videofile(unique_filename, codec="libx264", audio_codec="aac")
    
    print(f"Video saved as {unique_filename}")
    return unique_filename

# extract id
def extract_id_from_response(response_text):
    id_match = re.search(r'id:\s*(\d+)', response_text)
    if id_match:
        return id_match.group(1)
    else:
        return None

# extract name
def extract_name_from_response(response_text):
    name_match = re.search(r'name: (.*?)\n', response_text)
    if name_match:
        return name_match.group(1)
    else:
        return None
