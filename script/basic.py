import os
import re
from moviepy import AudioFileClip
import yaml
import json
import pathlib


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


class Prompt:
    _data = None

    @staticmethod
    def _load():
        if Prompt._data is None:
            with open("conf/prompt.yml", "r", encoding="utf-8") as file:
                Prompt._data = yaml.safe_load(file)

    @staticmethod
    def get(key):
        Prompt._load()
        if "prompt" in Prompt._data and key in Prompt._data["prompt"]:
            return Prompt._data["prompt"][key].strip()
        else:
            return None

    def get_sys(key):
        Prompt._load()
        if "sys" in Prompt._data and key in Prompt._data["sys"]:
            return Prompt._data["sys"][key].strip()
        else:
            return None

    def get_dev(key):
        Prompt._load()
        if "dev" in Prompt._data and key in Prompt._data["dev"]:
            return Prompt._data["dev"][key].strip()
        else:
            return None


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
    def json(string: str):
        try:
            return json.loads(re.search(r"\{[\s\S]*\}", string).group())
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def is_folder(name):
        folder = pathlib.Path(name)
        folder.mkdir(parents=True, exist_ok=True)
        if folder.exists():
            print(f"Folder '{name}' exists.")
        else:
            # This should not happen because exist_ok=True
            print(f"Error creating folder '{name}'.")

    @staticmethod
    def save_to_file(folder, filename, text):
        Utility.is_folder(folder)
        try:
            with open(f"{folder}/{filename}", "w") as file:
                file.write(text)
            print(f"Text saved successfully in {filename}.")
        except Exception as e:
            print(f"Error saving text: {e}")

    @staticmethod
    def save_to_file_json(folder, filename, text):
        return Utility.save_to_file(
            folder, filename, re.search(r"\{[\s\S]*\}", text).group()
        )

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
