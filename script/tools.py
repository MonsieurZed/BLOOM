import json
import os
from pathlib import Path
from moviepy.editor import AudioFileClip


def generate_audio_list(folder: str):

    supported_extensions = [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"]
    audio_list = []

    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = Path(file).suffix.lower()

            if file_extension in supported_extensions:
                try:
                    # Get audio duration
                    with AudioFileClip(file_path) as audio:
                        duration = round(audio.duration, 2)

                    # Add audio details to the list
                    audio_list.append(
                        {
                            "name": Path(file).stem,
                            "path": file_path,
                        }
                    )
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

        with open("audiolist.txt", "w", encoding="utf-8") as file:
            file.write("\n\n# Audio List\n")
            file.write(json.dumps(audio_list, indent=4, ensure_ascii=False))


generate_audio_list(r"D:\GIT\BLOOM\BLOOM\data\sounds")
