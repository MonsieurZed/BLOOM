import math
import os
import random
import string
from moviepy.editor import AudioFileClip
import yaml
import json
from pathlib import Path
from datetime import datetime


class Key:
    _data = None

    @staticmethod
    def _load():
        if Key._data is None:
            with open("conf/key.yml", "r", encoding="utf-8") as file:
                Key._data = yaml.safe_load(file)

    @staticmethod
    def get(key):
        Key._load()
        if key in Key._data and "api_key" in Key._data[key]:
            return Key._data[key]["api_key"].strip()
        else:
            return None


class Utility:
    @staticmethod
    def json_from_str(string: str):
        try:
            cleaned_text = string.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def make_folder(path):
        folder = Path(path)
        folder.mkdir(parents=True, exist_ok=True)
        if not folder.exists():
            print(f"Error creating folder '{path}'.")

    @staticmethod
    def save_to_file(folder, filename, text):
        Utility.make_folder(folder)
        try:
            with open(f"{folder}\{filename}", "w", encoding="utf-8") as file:
                file.write(text)
        except Exception as e:
            print(f"Error saving text: {e}")

    @staticmethod
    def save_to_file_json(folder, filename, data):
        try:
            Utility.save_to_file(
                folder, filename, json.dumps(data, ensure_ascii=False, indent=4)
            )
        except Exception as e:
            Utility.save_to_file(folder, filename, data)

    @staticmethod
    def get_duration(path_mp3):
        if not os.path.isfile(path_mp3):
            raise FileNotFoundError(f"The file '{path_mp3}' does not exist.")
        with AudioFileClip(path_mp3) as audio:
            duration = audio.duration
        return duration

    @staticmethod
    def remove_duplicates(input_string):
        items = [item.strip() for item in input_string.split(",")]
        unique_items = list(dict.fromkeys(items))
        return ", ".join(unique_items)

    @staticmethod
    def get_scene(folder: str, scene: str) -> str:
        folder_path = Path(folder)
        for file in folder_path.iterdir():
            if file.is_file() and f"S{int(scene):02}" in file.name:
                return str(file)
        return None

    @staticmethod
    def generate_random_name(prefix="file"):
        random_string = "".join(random.choices(string.ascii_letters, k=4))
        return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random_string}"

    @staticmethod
    def check_file_exists(file_path):
        if file_path is None:
            return False
        if os.path.exists(file_path):
            print(f"The file '{Path(file_path).name}' already exists.")
            return True
        else:
            return False

    @staticmethod
    def segment_cleaner(data):
        def round_up(value):
            if isinstance(value, float):
                return math.ceil(value * 100) / 100
            return value

        def filter_segment(segment):
            return {
                "text": segment.get("text"),
                "start": round_up(segment.get("start")),
                "end": round_up(segment.get("end")),
                "words": [
                    {
                        "word": word.get("word"),
                        "start": round_up(word.get("start")),
                        "end": round_up(word.get("end")),
                    }
                    for word in segment.get("words", [])
                ],
            }

        return [filter_segment(segment) for segment in data]
