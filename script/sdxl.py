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
        Anime = "1"
        Realistic = "1"

    def __init__(self, output_folder):
        self._output_folder = output_folder

    def generate(self, prompt, negatif, name=None, subname="", quantity=1):
        timer_start = time.time()

        Utility.is_folder(self._output_folder)

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
                print(f"Took in {time.time() - subtimer_start} seconds.")

    def generate_from_json(self, json_str, name=None, style=Style.Anime, quantity=1):
        print(json_str)
        json_obj = Utility.json(json_str)
        name = name if name else time.strftime("%m%d-%H%M")

        for prompt in json_obj["prompts"]:

            positive = prompt["prompt"]
            negative = (
                prompt["negative_prompt"]
                if "negative_prompt" in prompt
                else prompt["neagative_prompt"] if "neagative_prompt" in prompt else ""
            )

            self.generate(
                positive,
                negative,
                name,
                f"scene_{prompt['scene']}-iteration_{prompt['iteration']}",
                quantity,
            )

    def get_payload(
        self,
        positive_prompt,
        negative_prompt="",
        style=Style.Anime,
    ):
        positive = positive_prompt

        negative = "nsfw(1.5) , fantasy(1.5), surreal(1.5), cartoon, anime, CGI, 3D render, painting, illustration, unrealistic proportions, extra fingers, fused fingers, bad anatomy, deformed body parts, low quality, lowres, blurry, pixelated, grainy, abstract, distorted details, eerie,".join(
            negative_prompt
        )

        selection = ["Random Style"]
        if style is SDXL.Style.Anime:
            model = "animaPencilXL_v500.safetensors"
            selection = ["SAI Anime", "MRE Anime", "MRE Manga"]
        if style is SDXL.Style.Realistic:
            model = "sd_xl_base_1.0_0.9vae.safetensors"
            selection = ["Fooocus Enhance", "Fooocus Masterpiece", "Fooocus Cinematic"]

        return {
            "prompt": positive,
            "negative_prompt": Utility.remove_duplicates(negative),
            "style_selections": selection,
            "performance_selection": "Speed",
            "aspect_ratios_selection": "810*1440",
            "image_number": 1,
            "image_seed": -1,
            "sharpness": 2,
            "guidance_scale": 4,
            "base_model_name": model,
            "refiner_switch": 0.5,
            "loras": [
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
