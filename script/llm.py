from enum import Enum
import json
import time
from openai import OpenAI
from google import genai
from google.genai import types
from sympy import false
import yaml
from pathlib import Path
from script.basic import Utility
from PIL import Image
from io import BytesIO
from datetime import datetime


class Model(Enum):
    OpenAI_o4_Mini = "gpt-4o-mini"
    Perplexity_Sonar = "sonar"
    Gemini_2Flash = "gemini-2.0-flash"
    Gemini_Imagen = "gemini-2.0-flash"


class PromptLoader:
    class System(Enum):
        Empty = None
        Storyteller = "storyteller"
        Storyboard = "storyboard"
        SDXL = "sdxl"
        Sync = "sync"
        Publish = "publish"

    class Developper(Enum):
        Empty = None

    class User(Enum):
        Empty = None

    _data = {}

    @staticmethod
    def _load():
        if len(PromptLoader._data):
            return

        for item in Path("prompt").iterdir():
            if item.is_dir():
                for file in Path(item).iterdir():
                    if file.is_file():
                        with open(file, "r", encoding="utf-8") as item:
                            PromptLoader._data[file.stem] = item.read()

    @staticmethod
    def get(key: System):
        PromptLoader._load()
        if key is not None and key.value in PromptLoader._data:
            return PromptLoader._data[key.value]
        else:
            return None


class LLMGen:
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
        Utility.make_folder(self._output_folder)

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
        user: PromptLoader.User = PromptLoader.User.Empty,
        dev: PromptLoader.Developper = PromptLoader.Developper.Empty,
        sys: PromptLoader.System = PromptLoader.System.Empty,
    ):

        print(f"Asking {self._model.value} for {sys.name} ...", end="")

        if self._model is Model.Gemini_2Flash:
            return self._ask_gemini(prompt=prompt, user=user, dev=dev, sys=sys)

        message = []
        if self._model is Model.OpenAI_o4_Mini:
            if sys is not PromptLoader.System.Empty:
                message.append({"role": "system", "content": PromptLoader.get(sys)})
            if dev is not PromptLoader.Developper.Empty:
                message.append({"role": "developer", "content": PromptLoader.get(dev)})

        if self._model is Model.Perplexity_Sonar:
            if sys or dev:
                message.append(
                    {
                        "role": "system",
                        "content": f"{PromptLoader.get(sys)}\n{PromptLoader.get(dev)}",
                    }
                )

        message += [
            {
                "role": "user",
                "content": f"{PromptLoader.get(user)}\n{prompt.lstrip()}",
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
        user: PromptLoader.User = PromptLoader.User.Empty,
        dev: PromptLoader.Developper = PromptLoader.Developper.Empty,
        sys: PromptLoader.System = PromptLoader.System.Empty,
    ):
        timer = time.time()
        message: str = ""
        if dev is not PromptLoader.Developper.Empty:
            message += f"\n{PromptLoader.get(dev)}"
        if user is not PromptLoader.User.Empty:
            message += f"\n{PromptLoader.get(user)}"

        message += f"\n{prompt}"

        Utility.save_to_file(self._output_folder, sys.value + "_prompt", message)

        response = self._client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=PromptLoader.get(sys),
            ),
            contents=message,
        )

        Utility.save_to_file_json(
            self._output_folder, sys.value + "_result", response.text
        )

        print(f"{round(time.time() - timer, 2) }sec")
        return response.text

    def ask_image(self, name=None, select=false, quantity=1):
        with open(f"{self._output_folder}/sdxl_result", "r", encoding="utf-8") as file:
            json_obj = json.load(file)

        for prompt in json_obj["prompts"]:

            image_path = Utility.get_scene(self._output_folder, prompt["scene"])
            if image_path:
                print(
                    f"Image S{prompt['scene']} already exist ... Skipping S{prompt['scene']}.{prompt['iteration']}"
                )
                continue

            for index in range(1, quantity + 1):
                name = f"S{prompt['scene'].zfill(2)}_{prompt['iteration'].zfill(2)}{index:02}{datetime.now().microsecond:06}.png"
                try:
                    print(f"Generating {name}...", end="")
                    subtimer_start = time.time()

                    response = self._client.models.generate_images(
                        model="imagen-3.0-generate-002",
                        prompt=prompt["prompt"],
                        config=types.GenerateImagesConfig(
                            number_of_images=1, aspect_ratio="9:16"
                        ),
                    )

                    if not response.generated_images:
                        if response.error:
                            print(f"Error details: {response.error}")
                        continue

                    for generated_image in response.generated_images:
                        image = Image.open(BytesIO(generated_image.image.image_bytes))
                        image.save(f"{self._output_folder}/{name}")

                    print(f"{round(time.time() - subtimer_start, 2)} seconds.")

                except Exception as e:
                    print(f"{round(time.time() - subtimer_start, 2)} seconds. Failed")
                    print(f"{e}\n{prompt['prompt']}\n{e}")
                    continue

        if select:
            Utility.make_folder(f"{self._output_folder}/trash")
            input("Remove unwanted picture and press Enter to continue...")
            full = True
            scene_number = json_obj["prompts"][-1]["scene"]
            for index in range(1, int(scene_number)):
                file = Utility.get_scene(self._output_folder, index)
                if file is None:
                    full = False
                    break

            if full is False:
                self.ask_image(name, select, quantity)
