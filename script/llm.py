from enum import Enum
import time
from openai import OpenAI
from google import genai
from google.genai import types
import yaml
from pathlib import Path
from script.basic import Utility


class Model(Enum):
    OpenAI_o4_Mini = "gpt-4o-mini"
    Perplexity_Sonar = "sonar"
    Gemini_2Flash = "gemini-2.0-flash"


class Prompt:
    class System(Enum):
        Empty = None
        Storyteller = "storyteller.txt"
        Storyboard = "storyboard.txt"
        SDXL = "sdxl.txt"
        Sync = "sync.txt"

    class Developper(Enum):
        Empty = None

    class User(Enum):
        Empty = None

    _data = {}

    @staticmethod
    def _load():
        if len(Prompt._data):
            return

        for item in Path("prompt").iterdir():
            if item.is_dir():
                for file in Path(item).iterdir():
                    if file.is_file():
                        with open(file, "r", encoding="utf-8") as item:
                            Prompt._data[file.name] = item.read()

    @staticmethod
    def get(key: System):
        Prompt._load()
        if key is not None and key.value in Prompt._data:
            return Prompt._data[key.value]
        else:
            return None


class LLM:
    _client: object
    _model: str
    _log: bool
    _model: Model
    _output_folder: str

    def __init__(self, model: Model, output_folder, log=False):
        with open("conf/key.yml", "r") as file:
            self.key = yaml.safe_load(file)
        self._model = model
        self._output_folder = output_folder

        if model is Model.OpenAI_o4_Mini:
            self._client = OpenAI(
                api_key=self.key["openai"]["api_key"],
            )

        if model is Model.Perplexity_Sonar:
            self._client = OpenAI(
                api_key=self.key["perplexity"]["api_key"],
                base_url="https://api.perplexity.ai",
            )

        if model is Model.Gemini_2Flash:
            self._client = genai.Client(api_key=self.key["gemini"]["api_key"])

        self._model = model
        print(f"Model is : {self._model}")
        self._log = log

    def ask(
        self,
        prompt: str,
        user: Prompt.User = Prompt.User.Empty,
        dev: Prompt.Developper = Prompt.Developper.Empty,
        sys: Prompt.System = Prompt.System.Empty,
    ):

        print(f"Asking {self._model.value} for {sys.name} ...", end="")

        if self._model is Model.Gemini_2Flash:
            return self._ask_gemini(prompt=prompt, user=user, dev=dev, sys=sys)

        message = []
        if self._model is Model.OpenAI_o4_Mini:
            if sys is not Prompt.System.Empty:
                message.append({"role": "system", "content": Prompt.get(sys)})
            if dev is not Prompt.Developper.Empty:
                message.append({"role": "developer", "content": Prompt.get(dev)})

        if self._model is Model.Perplexity_Sonar:
            if sys or dev:
                message.append(
                    {
                        "role": "system",
                        "content": f"{Prompt.get(sys)}\n{Prompt.get(dev)}",
                    }
                )

        message += [
            {
                "role": "user",
                "content": f"{Prompt.get(user)}\n{prompt.lstrip()}",
            },
        ]

        print("Generating script...")
        completion = self._client.chat.completions.create(
            model=self._model.value, messages=message
        )

        print(f"Tokens used: {completion.usage.total_tokens}")
        print("Script generated.")

        Utility.save_to_file_json(
            self._output_folder, sys, completion.choices[0].message.content
        )

        return completion.choices[0].message.content

    def _ask_gemini(
        self,
        prompt: str,
        user: Prompt.User = Prompt.User.Empty,
        dev: Prompt.Developper = Prompt.Developper.Empty,
        sys: Prompt.System = Prompt.System.Empty,
    ):
        timer = time.time()
        message: str = ""
        if dev is not Prompt.Developper.Empty:
            message += f"\n{Prompt.get(dev)}"
        if user is not Prompt.User.Empty:
            message += f"\n{Prompt.get(user)}"

        message += f"\n{prompt}"

        Utility.save_to_file(self._output_folder, "prompt_" + sys.value, message)

        response = self._client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=Prompt.get(sys),
            ),
            contents=message,
        )

        Utility.save_to_file_json(
            self._output_folder, "result_" + sys.value, response.text
        )

        print(f"{round(time.time() - timer, 2) }sec")
        return response.text
