import os
import re
from moviepy.editor import AudioFileClip
import yaml
import json
import pathlib
import sys


def Folder_check():
    print("Checking...")
    folder_path = f"_output"
    try:
        os.mkdir(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_path}' already exists.")
    except OSError as error:
        print(f"Error creating folder: {error}")


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
            return json.loads(string)
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def make_folder(path):
        folder = pathlib.Path(path)
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
    def save_to_file_json(folder, filename, text):
        try:
            Utility.save_to_file(
                folder, filename, re.search(r"\{[\s\S]*\}", text).group()
            )
        except Exception as e:
            Utility.save_to_file(folder, filename, text)

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
        folder_path = pathlib.Path(folder)
        for file in folder_path.iterdir():
            if file.is_file() and f"S{int(scene):02}" in file.name:
                return str(file)
        return None
