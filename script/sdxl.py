from enum import Enum
import json
import requests
import yaml
import time

from script.basic import Utility


class SDXL:
    _url = "http://localhost:8888/v2/generation/text-to-image-with-ip"
    _headers = {"accept": "image/png", "Content-Type": "application/json"}
    _payload = None
    _output_folder = "_output"

    class Style(Enum):
        Anime = 0
        Realistic = 1
        Test = 2

    class Mood(Enum):
        Base = 0
        Horror = 1
        Suspense = 2

    def __init__(self, output_folder):
        self._output_folder = output_folder

    def generate(self, prompt, negatif, name=None, subname="", quantity=1):
        timer_start = time.time()

        Utility.make_folder(self._output_folder)

        for i in range(quantity):
            name = f"{subname}-version_{i+1}.png"
            print(f"Generating {name}...")
            if i > 1:
                subtimer_start = time.time()

            response = requests.post(
                self._url,
                json=self.get_payload(prompt, negatif),
                headers=self._headers,
            )

            with open(f"{self._output_folder}/{name}", "wb") as f:
                f.write(response.content)

            if i > 1:
                print(f"Took in {round(time.time() - subtimer_start, 2)} seconds.")

    def generate_from_json(
        self, json_str, name=None, style=Style.Anime, mood=Mood.Base, quantity=1
    ):
        json_obj = Utility.json_from_str(json_str)
        name = name if name else time.strftime("%m%d-%H%M")

        #  negatif = json_obj["prompts"]["negative_prompt"]
        payload_array = []
        for prompt in json_obj["prompts"]["scenes"]:
            positive = prompt["prompt"]
            subname = f"S{prompt['scene']}-I{prompt['iteration']}"
            Utility.make_folder(self._output_folder)
            for i in range(quantity):
                name = f"{subname}-V{i+1}.png"
                print(f"Generating image : {name} ... ", end="")

                timer = time.time()

                payload = self.get_payload(positive, "", style, mood)
                payload_array.append(
                    {
                        "scene": name,
                        "positif": payload["prompt"],
                        "negatif": payload["negative_prompt"],
                        "style_selections": payload["style_selections"],
                        "base_model_name": payload["base_model_name"],
                    }
                )
                response = requests.post(
                    self._url,
                    json=payload,
                    headers=self._headers,
                )

                with open(f"{self._output_folder}/{name}", "wb") as f:
                    f.write(response.content)

                print(f"{round(time.time() - timer, 2) }sec")

        Utility.save_to_file(
            self._output_folder, "payload.json", json.dumps(payload_array, indent=4)
        )

    def get_payload(
        self,
        positive_prompt="",
        negative_prompt="",
        style=Style.Anime,
        mood=Mood.Base,
    ):
        lora = []
        negatif = "nsfw, fantasy, surreal, unrealistic proportions, split screen, panel, comic, border, extra fingers, fused fingers, bad anatomy, deformed body parts, low quality, lowres, blurry, pixelated, grainy, abstract, distorted details, eerie"

        selection = ["Random Style"]
        if style is SDXL.Style.Test:
            positive = (
                positive_prompt
                + ", Bold outlines, vibrant colors, exaggerated expressions"
            )
            model = "animaPencilXL_v500.safetensors"
            selection = ["MRE Anime", "SAI Anime"]
            lora = (
                [
                    {
                        "enabled": "true",
                        "model_name": "sd_xl_offset_example-lora_1.0.safetensors",
                        "weight": 0.1,
                    },
                    {"enabled": "true", "model_name": "None", "weight": 1},
                    {"enabled": "true", "model_name": "None", "weight": 1},
                    {"enabled": "true", "model_name": "None", "weight": 1},
                    {"enabled": "true", "model_name": "None", "weight": 1},
                ],
            )

        if style is SDXL.Style.Realistic:
            model = "juggernautXL_v8Rundiffusion.safetensors"
            selection = ["Fooocus V2", "Fooocus Enhance", "Fooocus Sharp"]
            lora = (
                [
                    {
                        "enabled": "true",
                        "model_name": "sd_xl_offset_example-lora_1.0.safetensors",
                        "weight": 0.1,
                    }
                ],
            )

        if style is SDXL.Style.Anime:
            model = "hassakuXLIllustrious_betaV06.safetensors"
            selection = ["MRE Anime", "SAI Anime"]

        # if mood is SDXL.Mood.Horror:
        #     positive += ", Gritty, detailed depictions of fear, eerie abandoned places, and unsettling expressions with lifelike textures"
        # if mood is SDXL.Mood.Suspense:
        #     positive += ", Tense moments captured with cinematic lighting, expressive body language, and naturalistic settings"

        return {
            "prompt": positive_prompt,
            "negative_prompt": Utility.remove_duplicates(negatif),
            "negative_prompt": negatif,
            "style_selections": selection,
            "performance_selection": "Speed",
            "aspect_ratios_selection": "810*1440",
            "image_number": 1,
            "image_seed": -1,
            "sharpness": 4,
            "guidance_scale": 6,
            "base_model_name": model,
            "refiner_switch": 0.5,
            "loras": lora,
            "advanced_params": {
                "adaptive_cfg": 7,
                "adm_scaler_end": 0.3,
                "adm_scaler_negative": 0.8,
                "adm_scaler_positive": 1.5,
                "black_out_nsfw": "false",
                "canny_high_threshold": 128,
                "canny_low_threshold": 64,
                "clip_skip": 2,
                "controlnet_softness": 0.25,
                "debugging_cn_preprocessor": "false",
                "debugging_dino": "false",
                "debugging_enhance_masks_checkbox": "false",
                "debugging_inpaint_preprocessor": "false",
                "dino_erode_or_dilate": 0,
                "disable_intermediate_results": "false",
                "disable_preview": "false",
                "disable_seed_increment": "false",
                "freeu_b1": 1.01,
                "freeu_b2": 1.02,
                "freeu_enabled": "false",
                "freeu_s1": 0.99,
                "freeu_s2": 0.95,
                "inpaint_advanced_masking_checkbox": "true",
                "inpaint_disable_initial_latent": "false",
                "inpaint_engine": "v2.6",
                "inpaint_erode_or_dilate": 0,
                "inpaint_respective_field": 1,
                "inpaint_strength": 1,
                "invert_mask_checkbox": "false",
                "mixing_image_prompt_and_inpaint": "false",
                "mixing_image_prompt_and_vary_upscale": "false",
                "overwrite_height": -1,
                "overwrite_step": -1,
                "overwrite_switch": -1,
                "overwrite_upscale_strength": -1,
                "overwrite_vary_strength": -1,
                "overwrite_width": -1,
                "refiner_swap_method": "joint",
                "sampler_name": "dpmpp_2m_sde_gpu",
                "scheduler_name": "karras",
                "skipping_cn_preprocessor": "false",
                "vae_name": "Default (model)",
            },
            "save_meta": "true",
            "meta_scheme": "fooocus",
            "save_extension": "png",
            "save_name": "",
            "read_wildcards_in_order": "false",
            "require_base64": "false",
            "async_process": "false",
            "webhook_url": "",
            "image_prompts": [],
        }
