from enum import Enum
import json
from pathlib import Path
import shutil
import os
import json
import shutil
from pathlib import Path
from moviepy.editor import AudioFileClip


from script.basic import Utility


class Bloom:
    _current_language = None
    _current_folder = None  # Static variable to hold the output folder in memory
    _data_folder = "data"
    _common = "common"
    _base: json = None

    class SharedFile(Enum):
        Base_json: str = "base.json"

    class OutputFile(Enum):
        Empty = None
        Audio_mp3: str = "audio.mp3"
        Audio_json: str = "audio.json"
        Bloom_mp3: str = "bloom.wav"
        Part_mp4: str = "part.mp4"
        Final_mp4: str = "final.mp4"
        Sound_mp3: str = "sound.mp3"

    class Prompt:
        class System(Enum):
            Empty = None
            Storyteller = "storyteller"
            SoundDesigner = "sounddesigner"
            Storyboard = "storyboard"
            SDXL = "sdxl"
            ImageSync = "imagesync"
            Publish = "publish"
            Subschecker = "subschecker"
            Translate = "translate"
            Test = "test"

        class Developper(Enum):
            Empty = None

        class User(Enum):
            Empty = None

        class Suffix(Enum):
            Empty = None
            Result = "_result"
            Promt = "prompt"

    class Model(Enum):
        OpenAI_o4_Mini = "gpt-4o-mini"
        Perplexity_Sonar = "sonar"
        Gemini_2Flash = "gemini-2.0-flash"
        Gemini_Imagen = "imagen-3.0-generate-002"

    class Data(Enum):
        Intro = "intro.png"
        Outro = "outro.png"
        Musique = "suspense.mp3"

    class Languages(Enum):
        Empty = None
        English = "English"
        French = "French"
        Spanish = "Spanish"

    @staticmethod
    def set_video(folder: str, language: Languages = Languages.English) -> json:
        Bloom._current_folder = folder
        Bloom._current_language = language
        Utility.make_folder(folder + "\\" + language.value)
        Utility.make_folder(folder + "\\" + Bloom._common)
        Utility.make_folder(folder + "\\" + "trash")
        with open(
            Bloom._current_folder + "\\" + Bloom.SharedFile.Base_json.value,
            "r",
            encoding="utf-8",
        ) as file:
            Bloom._base = json.load(file)
        print(f"working in {Bloom.get_folder_path()}")
        return Bloom._base

    @staticmethod
    def get_folder_path() -> str:
        path = Bloom._current_folder + "\\" + Bloom._current_language.value
        if path is None:
            raise ValueError("Output folder has not been set.")
        return path

    @staticmethod
    def get_output_file_path(file: OutputFile) -> str:
        return Bloom.get_folder_path() + "\\" + file.value

    @staticmethod
    def get_prompt_file_path(
        file: Prompt.System, suffix: Prompt.Suffix = Prompt.Suffix.Result
    ) -> str:
        return Bloom.get_folder_path() + "\\" + file.value + suffix.value

    @staticmethod
    def get_data_file_path(file: Data):
        return Bloom._data_folder + "\\" + file.value

    @staticmethod
    def get_common_folder():
        path = Bloom._current_folder + "\\" + Bloom._common
        if path is None:
            raise ValueError("Output folder has not been set.")
        return path

    @staticmethod
    def get_root_file_path(file: OutputFile, prefix: Languages = Languages.Empty):
        if not prefix:
            path = Bloom._current_folder + "\\" + file.value
        else:
            path = Bloom._current_folder + "\\" + prefix.value + "_" + file.value
        if path is None:
            raise ValueError("Output folder has not been set.")
        return path

    @staticmethod
    def copy_file_from(
        filename,
        from_language: Languages = Languages.English,
    ):
        from_folder = Path(Bloom._current_folder + "\\" + from_language.value)
        to_folder = Path(Bloom._current_folder + "\\" + Bloom._current_language.value)
        for file in from_folder.iterdir():
            if file.is_file() and filename in file.name:
                destination = to_folder / file.name
                shutil.copy(file, destination)
                print(f"Fichier copié : {file} -> {destination}")
                return str(destination)
