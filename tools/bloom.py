import os, shutil, json
from enum import Enum
from pathlib import Path
from moviepy.editor import AudioFileClip
from tools.utility import Utility


class Bloom:
    _current_language = None
    _current_folder = None  # Static variable to hold the output folder in memory
    _data_folder = "data"
    _sound_folder = "sounds"
    _common = "common"
    _base: json = None

    class Languages(Enum):
        Empty = None
        English = "English"
        French = "French"
        Spanish = "Spanish"

    class SharedFile(Enum):
        Base_json: str = "base.json"

    class OutputFile(Enum):
        Empty = None
        Audio_mp3: str = "audio.mp3"
        Audio_json: str = "audio.json"
        Part_mp4: str = "part.mp4"
        Final_mp4: str = "final.mp4"
        Sound_mp3: str = "sound.mp3"

    class Data(Enum):
        Outro_audio: str = "BipBloom.mp3"
        Intro_img = "intro.png"
        Outro_img = "outro.png"
        music = "suspense.mp3"
        Sound_Folder = "sounds"

    class Prompt:
        class System(Enum):
            Empty = None
            Storyteller = "storyteller"
            SoundDesigner = "sounddesigner"
            Storyboard = "storyboard"
            ImageGen = "imagen"
            ImageSync = "imagesync"
            Publish = "publish"
            Subschecker = "subschecker"
            Translate = "translate"
            Test = "test"

        class Suffix(Enum):
            Empty = None
            Result = "_result"
            Promt = "prompt"

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
    def get_sound_folder():
        path = Bloom._data_folder + "\\" + Bloom._sound_folder
        if path is None:
            raise ValueError("Output folder has not been set.")
        return path

    @staticmethod
    def get_sound_path(sound: str):
        return Bloom.get_sound_folder() + "\\" + sound

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

    @staticmethod
    def get_audio_list():
        folder = Bloom._data_folder + "\\" + "sounds"
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

                        # Add audio details to the list with relative paths
                        audio_list.append(
                            {
                                "name": Path(file).stem,
                                "path": os.path.relpath(
                                    file_path, folder
                                ),  # Relative path
                                "duration": duration,
                            }
                        )
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

            return json.dumps(audio_list, indent=4, ensure_ascii=False)
