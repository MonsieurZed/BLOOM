import json
from enum import Enum
from pathlib import Path
from shutil import copyfile


class Dictionnary:
    class Languages(Enum):
        Empty = None
        English = "English"
        French = "French"
        Spanish = "Spanish"

    class Style(Enum):
        Empy = None
        Photorealistic = "photorealistic"
        Anime = "anime"

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

    class Prompt(Enum):
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

    class Prompt_Suffix(Enum):
        Empty = None
        Result = "_result"
        Promt = "_ask"


class Bloom:
    _base_path: Path
    _data_path: Path
    _id: int = -1
    _dict: dict = {}
    _language: Dictionnary.Languages = None
    _style: Dictionnary.Style = None
    date: str = "Unknown Date"
    place: str = "Unknown Location"
    story: str = None

    def __init__(
        self,
        base_path,
        data_path,
        language: Dictionnary.Languages = Dictionnary.Languages.Empty,
        style: Dictionnary.Style = Dictionnary.Style.Empy,
    ):
        self._base_path = Path(base_path) / "base.json"
        self._data_path = Path(data_path)

        # Create a backup of base_path if it doesn't exist
        backup_path = self._base_path.with_suffix(".bak.json")
        if not backup_path.exists():
            copyfile(self._base_path, backup_path)

        with open(self._base_path, "r", encoding="utf-8") as file:
            base = json.load(file)

        if base.get("story") is None:
            raise ValueError("Story not found in base.json")

        self._id = base.get("id", -1)
        self.place = base.get("place", "Unknown Location")
        self.date = base.get("date", "Unknown Date")
        self.story = base.get("story", None)
        self._dict = base.get("dict", {})
        self._language = language
        self._style = style

    def __update__(self):
        with open(self._base_path, "r", encoding="utf-8") as file:
            payload = json.load(file)
        payload["dict"] = self._dict
        with open(self._base_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4, ensure_ascii=False)

    def add(self, key: Dictionnary.OutputFile | Dictionnary.Prompt, value):
        if value is None:
            raise ValueError("Value cannot be None")
        self._dict[key.value] = value
        self.__update__()

    def get(self, key: Dictionnary.OutputFile | Dictionnary.Prompt):
        if key.value in self._dict:
            print(f"Key {key.value} found in the dictionary.")
            return self._dict[key.value]
        else:
            print(f"Key {key.value} not found in the dictionary.")
            None

    def import_from(
        self, key: Dictionnary.OutputFile | Dictionnary.Prompt, source: "Bloom"
    ):
        if key.value in source._dict:
            self._dict[key.value] = source._dict[key.value]
        else:
            raise KeyError(f"Key {key.value} not found in the source dictionary.")

    def get_root(self) -> Path:
        return self._base_path.parent

    def get_img_folder(self) -> Path:
        img = self.get_root() / "img"
        if not img.exists():
            img.mkdir(parents=True, exist_ok=True)
        return img

    def get_language_folder(
        self,
        key: Dictionnary.OutputFile | Dictionnary.Prompt = None,
    ) -> Path:
        folder = self.get_root() / self._language.value
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        if key is not None:
            return folder / key.value
        return folder

    def get_log_folder(self) -> Path:
        folder = self.get_language_folder() / "log"
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    def get_data_folder(
        self,
        key: Dictionnary.Data = None,
    ) -> Path:
        if key is not None:
            return self._data_path / key.value
        folder = self._data_path
        if key is not Dictionnary.OutputFile.Empty:
            return folder / key.value
        return folder
