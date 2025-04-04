import json, os, re, time, yaml
from io import BytesIO
from PIL import Image
from enum import Enum
from openai import OpenAI
from google import genai
from pathlib import Path
from datetime import datetime
from google.genai import types
from concurrent.futures import ThreadPoolExecutor, as_completed
from tools.utility import Utility
from tools.bloom import Dictionnary


class PromptLoader:
    _data = {}

    @staticmethod
    def _load():
        if len(PromptLoader._data):
            return

        for file in Path("prompt").iterdir():
            if file.is_file():
                with open(file, "r", encoding="utf-8") as item:
                    PromptLoader._data[file.stem] = item.read()

    @staticmethod
    def get(key: Dictionnary.Prompt):
        PromptLoader._load()
        if key is not None and key.value in PromptLoader._data:
            return PromptLoader._data[key.value]
        else:
            return None


class AIGen:

    class LLMModel(Enum):
        OpenAI_o4_Mini = "gpt-4o-mini"
        Perplexity_Sonar = "sonar"
        Gemini_2Flash = "gemini-2.0-flash"

    class ImageModel(Enum):
        Gemini_Imagen = "imagen-3.0-generate-002"

    _client: object
    _log: bool
    _llm_model: LLMModel
    _image_model: ImageModel

    def __init__(
        self,
        llm_model: LLMModel = LLMModel.Gemini_2Flash,
        image_model: ImageModel = ImageModel.Gemini_Imagen,
    ):
        print("Loading AI Gen ...")
        with open("conf/key.yml", "r") as file:
            self.key = yaml.safe_load(file)

        if llm_model is AIGen.LLMModel.OpenAI_o4_Mini:
            self._client = OpenAI(
                api_key=self.key["openai"]["api_key"],
            )

        if llm_model is AIGen.LLMModel.Perplexity_Sonar:
            self._client = OpenAI(
                api_key=self.key["perplexity"]["api_key"],
                base_url="https://api.perplexity.ai",
            )

        if llm_model is AIGen.LLMModel.Gemini_2Flash:
            self._client = genai.Client(api_key=self.key["gemini"]["api_key"])

        self._llm_model = llm_model
        self._image_model = image_model
        print(f"LLM Model is : {self._llm_model}")

    def ask_json(
        self,
        prompt: json,
        sys: Dictionnary.Prompt = Dictionnary.Prompt.Empty,
        sys_custom: str = None,
        output_path: str = None,
    ) -> json:
        if output_path is None:
            print("Output path must be set")

        print(f"Asking {self._llm_model.name} for {sys.name} ...", end="")

        timer = time.time()
        system = PromptLoader.get(sys)
        if sys_custom:
            system += sys_custom

        Utility.save_to_file_json(output_path, sys.value + "_prompt", prompt)

        response = self._client.models.generate_content(
            model=self._llm_model.value,
            config=types.GenerateContentConfig(
                system_instruction=system,
            ),
            contents=json.dumps(prompt),
        )

        match = re.search(r"```json\n(.*?)\n```", response.text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return_val = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
        else:
            print("No JSON found.")

        Utility.save_to_file_json(output_path, sys.value + "_result", return_val)

        print(f"{round(time.time() - timer, 2) }sec")
        return return_val

    def ask_image(
        self,
        prompts: json,
        output_folder: str,
        name=None,
        select=False,
        quantity=1,
    ):
        print(f"Starting Image generation ...")
        timer = time.time()

        def process_prompt(prompt, prompt_index=0):
            """
            Process a single prompt: generate images and save them.
            """
            if Utility.check_file_exists(
                Utility.get_scene(output_folder, prompt["scene"])
            ):
                return

            for index in range(1, quantity + 1):
                name = f"S{prompt['scene'].zfill(2)}_{prompt_index:02}{index:02}{datetime.now().microsecond:06}.png"

                try:

                    subtimer_start = time.time()

                    response = self._client.models.generate_images(
                        model=self._image_model.value,
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
                        image.save(f"{output_folder}/{name}")

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
            futures = [executor.submit(process_prompt, prompt) for prompt in prompts]
            for future in as_completed(futures):
                future.result()  # Wait for each thread to complete

        print(f"Images generated  in {round(time.time() - timer, 2)} seconds.")

        if select:
            Utility.make_folder(f"{output_folder}/trash")
            rt = input(
                "Remove unwanted pictures and  press enter to continue...\n Enter 'c' to continue > "
            )
            if "c" not in rt:
                self.ask_image(name, select, quantity)

    def quick_image(self, prompt):
        response = self._client.models.generate_images(
            model=Dictionnary.Model.Gemini_Imagen.value,
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
        sys: Dictionnary.Prompt = Dictionnary.Prompt.Empty,
        sys_custom: str = None,
        output_path: str = None,
    ):

        print(f"Asking {self._llm_model.value} for {sys.name} ...", end="")

        timer = time.time()
        message: str = ""
        message += f"\n{prompt}"

        system = PromptLoader.get(sys)
        if sys_custom:
            system += sys_custom

        response = self._client.models.generate_content(
            model=AIGen.LLMModel.Gemini_2Flash.value,
            config=types.GenerateContentConfig(
                system_instruction=PromptLoader.get(sys),
            ),
            contents=message,
        )

        Utility.save_to_file_json(output_path, sys.value + "_result", response.text)

        print(f"{round(time.time() - timer, 2) }sec")
        return response.text

    # message = []
    #     if self._model is LLMGen.Model.OpenAI_o4_Mini:
    #         if sys is not Dictionnary.Prompt.Empty:
    #             message.append({"role": "system", "content": PromptLoader.get(sys)})
    #         if dev is not Dictionnary.Prompt.Developper.Empty:
    #             message.append({"role": "developer", "content": PromptLoader.get(dev)})

    #     if self._model is LLMGen.Model.Perplexity_Sonar:
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
    #     sys: Bloom.Prompt = Bloom.Prompt.Empty,
    # ):
