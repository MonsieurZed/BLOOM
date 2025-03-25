
import requests

json_data = {
  "prompts": [
  {
    "scene": 1,
    "prompt": "A lone man stands atop a desolate hill. The sky looms dark, heavy storm clouds rolling in. The air is thick with tension. The landscape is vast, empty, eerie. The man looks small against the incoming chaos. Cinematic, moody lighting, muted colors, high contrast."
  },
  {
    "scene": 2,
    "prompt": "The wind howls through the trees. Dark storm clouds churn above. The branches twist violently, the grass bends under the force. Shadows flicker across the ground. The atmosphere is ominous, charged, unsettling. Cinematic, dynamic composition, high contrast."
  },
  {
    "scene": 3,
    "prompt": "Raindrops begin to fall. The dirt path turns muddy, small puddles forming. The man stands still, his clothes damp, his hair sticking to his forehead. The world around him is drenched in a cold, bluish hue. His expression is unreadable. Cinematic, dark tones, eerie ambiance."
  },
  {
    "scene": 4,
    "prompt": "The man raises his selfie stick, smiling. His eyes reflect the storm, unaware of the danger. His phone screen glows faintly against the gloom. The metal rod gleams slightly in the dim light. A false sense of peace before disaster. Cinematic framing, contrast between calm and chaos."
  },
  {
    "scene": 5,
    "prompt": "A blinding white flash splits the sky. Lightning strikes down with raw, unstoppable force. The entire scene is illuminated in stark, terrifying detail. The man’s silhouette is caught mid-motion, frozen in the instant before impact. High-intensity light, chaotic energy, dramatic composition."
  },
  {
    "scene": 6,
    "prompt": "The man collapses to the ground. Smoke rises from his burnt clothing. His body is lifeless, scorched. The air smells of ozone and burned flesh. The storm rages on, indifferent. The moment is both horrifying and surreal. Dark tones, unsettling realism, cinematic."
  },
  {
    "scene": 7,
    "prompt": "A close-up of the ground. A shattered phone lies in the dirt, its screen cracked, rainwater pooling around it. The selfie never taken. Silence after the storm. The scene is eerie, empty, final. Subtle lighting, muted colors, melancholic atmosphere."
  }
]

    }
    
url = "http://localhost:8888/v2/generation/text-to-image-with-ip" 
# Request headers
headers = {"accept": "image/png", "Content-Type": "application/json"}

# Request payload
payload = {
    "prompt": "TBD",
    "negative_prompt": "",
    "style_selections": [
        "SAI Anime",
      	"MRE Anime",
       	"MRE Manga"
    ],
    "performance_selection": "Speed",
    "aspect_ratios_selection": "810*1440",
    "image_number": 1,
    "image_seed": -1,
    "sharpness": 2,
    "guidance_scale": 4,
    "base_model_name": "animaPencilXL_v500.safetensors",
    "refiner_switch": 0.5,
    "loras": [
        {"enabled": True, "model_name": "sd_xl_offset_example-lora_1.0.safetensors", "weight": 0.1},
        {"enabled": True, "model_name": "None", "weight": 1},
        {"enabled": True, "model_name": "None", "weight": 1},
        {"enabled": True, "model_name": "None", "weight": 1},
        {"enabled": True, "model_name": "None", "weight": 1},
    ],
    "advanced_params": {
        "adaptive_cfg": 7,
        "adm_scaler_end": 0.3,
        "adm_scaler_negative": 0.8,
        "adm_scaler_positive": 1.5,
        "black_out_nsfw": False,
        "canny_high_threshold": 128,
        "canny_low_threshold": 64,
        "clip_skip": 2,
        "controlnet_softness": 0.25,
        "debugging_cn_preprocessor": False,
        "debugging_dino": False,
        "debugging_enhance_masks_checkbox": False,
        "debugging_inpaint_preprocessor": False,
        "dino_erode_or_dilate": 0,
        "disable_intermediate_results": False,
        "disable_preview": False,
        "disable_seed_increment": False,
        "freeu_b1": 1.01,
        "freeu_b2": 1.02,
        "freeu_enabled": False,
        "freeu_s1": 0.99,
        "freeu_s2": 0.95,
        "inpaint_advanced_masking_checkbox": True,
        "inpaint_disable_initial_latent": False,
        "inpaint_engine": "v2.6",
        "inpaint_erode_or_dilate": 0,
        "inpaint_respective_field": 1,
        "inpaint_strength": 1,
        "invert_mask_checkbox": False,
        "mixing_image_prompt_and_inpaint": False,
        "mixing_image_prompt_and_vary_upscale": False,
        "overwrite_height": -1,
        "overwrite_step": -1,
        "overwrite_switch": -1,
        "overwrite_upscale_strength": -1,
        "overwrite_vary_strength": -1,
        "overwrite_width": -1,
        "refiner_swap_method": "joint",
        "sampler_name": "dpmpp_2m_sde_gpu",
        "scheduler_name": "karras",
        "skipping_cn_preprocessor": False,
        "vae_name": "Default (model)",
    },
    "save_meta": True,
    "meta_scheme": "fooocus",
    "save_extension": "png",
    "save_name": "",
    "read_wildcards_in_order": False,
    "require_base64": False,
    "async_process": False,
    "webhook_url": "",
    "image_prompts": [],
}


def generate_images_from_prompts(prompts):
    for scene in prompts["prompts"]:
        scene_number = scene["scene"]
        payload["prompt"] = scene["prompt"]
        
        print(f"Generating image for Scene {scene_number}...")
        print(f"Prompt: {payload['prompt']}\n")
        
        for i in range(4):
            response = requests.post(url, json=payload, headers=headers)
            with open(f"{scene_number}_{i}.png", "wb") as f:
                f.write(response.content)




generate_images_from_prompts(json_data)
