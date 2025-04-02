import json
import time
from openai import OpenAI
from google import genai
from google.genai import types
import yaml
from pathlib import Path
from script.basic import Utility
from PIL import Image
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from script.bloom import Bloom


class PromptLoader:
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
    def get(key: Bloom.Prompt.System):
        PromptLoader._load()
        if key is not None and key.value in PromptLoader._data:
            return PromptLoader._data[key.value]
        else:
            return None


class LLMGen:
    _client: object
    _model: str
    _log: bool
    _model: Bloom.Model
    _output_folder: str

    def __init__(self, model: Bloom.Model, output_folder, log=False):
        with open("conf/key.yml", "r") as file:
            self.key = yaml.safe_load(file)
        self._model = model
        self._output_folder = output_folder
        Utility.make_folder(self._output_folder)

        if model is Bloom.Model.OpenAI_o4_Mini:
            self._client = OpenAI(
                api_key=self.key["openai"]["api_key"],
            )

        if model is Bloom.Model.Perplexity_Sonar:
            self._client = OpenAI(
                api_key=self.key["perplexity"]["api_key"],
                base_url="https://api.perplexity.ai",
            )

        if model is Bloom.Model.Gemini_2Flash:
            self._client = genai.Client(api_key=self.key["gemini"]["api_key"])

        self._model = model
        print(f"Model is : {self._model}")
        self._log = log

    def ask(
        self,
        prompt: str,
        user: Bloom.Prompt.User = Bloom.Prompt.User.Empty,
        dev: Bloom.Prompt.Developper = Bloom.Prompt.Developper.Empty,
        sys: Bloom.Prompt.System = Bloom.Prompt.System.Empty,
        output_path: str = None,
    ):

        print(f"Asking {self._model.value} for {sys.name} ...", end="")

        timer = time.time()
        message: str = ""
        if dev is not Bloom.Prompt.Developper.Empty:
            message += f"\n{Bloom.Prompt.get(dev)}"
        if user is not Bloom.Prompt.User.Empty:
            message += f"\n{Bloom.Prompt.get(user)}"

        message += f"\n{prompt}"

        Utility.save_to_file(Bloom.get_folder_path(), sys.value + "_prompt", message)

        response = self._client.models.generate_content(
            model=Bloom.Model.Gemini_2Flash.value,
            config=types.GenerateContentConfig(
                system_instruction=PromptLoader.get(sys),
            ),
            contents=message,
        )

        Utility.save_to_file_json(
            Bloom.get_folder_path(), sys.value + "_result", response.text
        )

        print(f"{round(time.time() - timer, 2) }sec")
        return response.text

    def ask_image(self, name=None, select=False, quantity=1):
        print(f"Starting Image generation ...")
        timer = time.time()
        with open(
            Bloom.get_prompt_file_path(Bloom.Prompt.System.SDXL), "r", encoding="utf-8"
        ) as file:
            json_obj = json.load(file)

        def process_prompt(prompt, prompt_index=0):
            """
            Process a single prompt: generate images and save them.
            """
            if Utility.check_file_exists(
                Utility.get_scene(Bloom.get_common_folder(), prompt["scene"])
            ):
                return

            for index in range(1, quantity + 1):
                name = f"S{prompt['scene'].zfill(2)}_{prompt_index:02}{index:02}{datetime.now().microsecond:06}.png"

                try:

                    subtimer_start = time.time()

                    response = self._client.models.generate_images(
                        model=Bloom.Model.Gemini_Imagen.value,
                        prompt=prompt["prompt"][prompt_index],
                        config=types.GenerateImagesConfig(
                            number_of_images=1, aspect_ratio="9:16"
                        ),
                    )

                    if not response.generated_images:
                        if response.error:
                            print(f"Error details: {response.error}")
                        raise

                    for generated_image in response.generated_images:
                        image = Image.open(BytesIO(generated_image.image.image_bytes))
                        image.save(f"{Bloom.get_common_folder()}/{name}")

                    print(
                        f"Generating {name} > {round(time.time() - subtimer_start, 2)} seconds."
                    )

                except Exception as e:
                    print(
                        f"Generating {name} > {round(time.time() - subtimer_start, 2)} seconds. Failed"
                    )
                    print(f"{e}\n{prompt['prompt']}\n{e}")
                    if prompt_index < len(prompt):
                        process_prompt(prompt, prompt_index + 1)

        # Use ThreadPoolExecutor to process prompts in parallel
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_prompt, prompt)
                for prompt in json_obj["prompts"]
            ]
            for future in as_completed(futures):
                future.result()  # Wait for each thread to complete

        print(f"Images generated  in {round(time.time() - timer, 2)} seconds.")

        if select:
            Utility.make_folder(f"{self._output_folder}/trash")
            input("Remove unwanted pictures and press Enter to continue...")
            full = True
            scene_number = json_obj["prompts"][-1]["scene"]
            for index in range(1, int(scene_number)):
                file = Utility.get_scene(self._output_folder, index)
                if file is None:
                    full = False
                    break

            if full is False:
                self.ask_image(name, select, quantity)

    def quick_image(self, prompt):
        response = self._client.models.generate_images(
            model=Bloom.Model.Gemini_Imagen.value,
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="9:16"),
        )
        if not response.generated_images:
            if response.error:
                print(f"Error details: {response.error}")

        for generated_image in response.generated_images:
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            name = f"{self._output_folder}/{Utility.generate_random_name('IMG')}.png"
            image.save(name)

    def quick_ask(
        self,
        prompt: str,
        user: Bloom.Prompt.User = Bloom.Prompt.User.Empty,
        dev: Bloom.Prompt.Developper = Bloom.Prompt.Developper.Empty,
        sys: Bloom.Prompt.System = Bloom.Prompt.System.Empty,
        output_path: str = None,
    ):

        print(f"Asking {self._model.value} for {sys.name} ...", end="")

        timer = time.time()
        message: str = ""
        if dev is not Bloom.Prompt.Developper.Empty:
            message += f"\n{Bloom.Prompt.get(dev)}"
        if user is not Bloom.Prompt.User.Empty:
            message += f"\n{Bloom.Prompt.get(user)}"

        message += f"\n{prompt}"

        response = self._client.models.generate_content(
            model=Bloom.Model.Gemini_2Flash.value,
            config=types.GenerateContentConfig(
                system_instruction=PromptLoader.get(sys),
            ),
            contents=message,
        )

        Utility.save_to_file_json(output_path, sys.value + "_result", response.text)

        print(f"{round(time.time() - timer, 2) }sec")
        return response.text

    # message = []
    #     if self._model is Bloom.Model.OpenAI_o4_Mini:
    #         if sys is not Bloom.Prompt.System.Empty:
    #             message.append({"role": "system", "content": PromptLoader.get(sys)})
    #         if dev is not Bloom.Prompt.Developper.Empty:
    #             message.append({"role": "developer", "content": PromptLoader.get(dev)})

    #     if self._model is Bloom.Model.Perplexity_Sonar:
    #         if sys or dev:
    #             message.append(
    #                 {
    #                     "role": "system",
    #                     "content": f"{PromptLoader.get(sys)}\n{PromptLoader.get(dev)}",
    #                 }
    #             )

    #     message += [
    #         {
    #             "role": "user",
    #             "content": f"{PromptLoader.get(user)}\n{prompt.lstrip()}",
    #         },
    #     ]

    #     print("Generating script...")
    #     completion = self._client.chat.completions.create(
    #         model=self._model.value, messages=message
    #     )

    #     print(f"Tokens used: {completion.usage.total_tokens}")
    #     print("Script generated.")

    #     Utility.save_to_file_json(
    #         self._output_folder, sys, completion.choices[0].message.content
    #     )

    #     return completion.choices[0].message.content

    # def _ask_gemini(
    #     self,
    #     prompt: str,
    #     user: Bloom.Prompt.User = Bloom.Prompt.User.Empty,
    #     dev: Bloom.Prompt.Developper = Bloom.Prompt.Developper.Empty,
    #     sys: Bloom.Prompt.System = Bloom.Prompt.System.Empty,
    # ):
