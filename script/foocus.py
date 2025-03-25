import requests
import json
import yaml


def generate_images_from_prompts(name, quantity=1):
    with open(f"_output/{name}/2_prompt.json", "r") as file:
        json_data = json.load(file)

    url = "http://localhost:8888/v2/generation/text-to-image-with-ip"
    # Request headers
    headers = {"accept": "image/png", "Content-Type": "application/json"}

    with open("conf/foocus.yml", "r") as yaml_file:
        payload = yaml.safe_load(yaml_file)

    for scene in json_data["prompts"]:
        scene_number = scene["scene"]
        payload["prompt"] = scene["description"]

        print(f"Generating image for Scene {scene_number}...")
        print(f"Prompt: {payload['prompt']}\n")

        for i in range(quantity):
            response = requests.post(url, json=payload, headers=headers)
            with open(f"_output/{name}/scene{scene_number}_v{i}.png", "wb") as f:
                f.write(response.content)
