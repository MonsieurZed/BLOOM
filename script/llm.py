from enum import Enum
from openai import OpenAI
from google import genai
from google.genai import types
import yaml

from script.basic import Prompt, Utility


class Model(Enum):
    OpenAI_o4_Mini = "gpt-4o-mini"
    Perplexity_Sonar = "sonar"
    Gemini_2Flash = "gemini-2.0-flash"


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

    def ask(self, user, sys=None, dev=None):

        if self._model is Model.Gemini_2Flash:
            return self._ask_gemini(user, sys, dev)

        message = []
        if self._model is Model.OpenAI_o4_Mini:
            if sys:
                message.append({"role": "system", "content": Prompt.get_sys(sys)})
            if dev:
                message.append({"role": "developer", "content": Prompt.get_sys(dev)})

        if self._model is Model.Perplexity_Sonar:
            if sys or dev:
                message.append(
                    {
                        "role": "system",
                        "content": f"{Prompt.get_dev(sys)}\n{Prompt.get_dev(dev)}",
                    }
                )

        message += [
            {
                "role": "user",
                "content": user,
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

    def _ask_gemini(self, user, sys=None, dev=None):

        print("Generating script...")

        response = self._client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=Prompt.get_sys(sys),
            ),
            contents=f"{dev} Voici la scene :  {user}",
        )

        Utility.save_to_file_json(self._output_folder, sys, response.text)

        return response.text
