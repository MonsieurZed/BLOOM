import requests
import json
import time
import os

class FoocusClient:
    def __init__(self, host="http://127.0.0.1", port=7865):
        """Initialize the Foocus client.
        
        Args:
            host (str): The host address of the Foocus server
            port (int): The port number of the Foocus server
        """
        self.base_url = f"{host}:{port}"
        
    def generate_image(self, prompt, negative_prompt="", style_preset="None", 
                      image_number=1, image_seed=-1, sharpness=2.0, 
                      guidance_scale=7.5, base_model_name="", 
                      refiner_model_name="", refiner_switch=0.8,
                      loras=None, save_path="outputs"):
        """Generate an image using Foocus.
        
        Args:
            prompt (str): The text prompt for image generation
            negative_prompt (str): The negative prompt
            style_preset (str): The style preset to use
            image_number (int): Number of images to generate
            image_seed (int): Seed for image generation (-1 for random)
            sharpness (float): Sharpness value
            guidance_scale (float): Guidance scale for generation
            base_model_name (str): Name of the base model
            refiner_model_name (str): Name of the refiner model
            refiner_switch (float): Refiner switch value
            loras (list): List of LoRA configurations
            save_path (str): Path to save generated images
            
        Returns:
            list: List of paths to generated images
        """
        if loras is None:
            loras = []
            
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "style_preset": style_preset,
            "image_number": image_number,
            "image_seed": image_seed,
            "sharpness": sharpness,
            "guidance_scale": guidance_scale,
            "base_model_name": base_model_name,
            "refiner_model_name": refiner_model_name,
            "refiner_switch": refiner_switch,
            "loras": loras,
            "save_path": save_path
        }
        
        try:
            # Send the generation request
            response = requests.post(f"{self.base_url}/run", json=payload)
            response.raise_for_status()
            
            # Get the task ID
            task_id = response.json()
            
            # Poll for results
            while True:
                status_response = requests.get(f"{self.base_url}/status/{task_id}")
                status_response.raise_for_status()
                status = status_response.json()
                
                if status.get("status") == "completed":
                    return status.get("output", [])
                elif status.get("status") == "failed":
                    raise Exception(f"Generation failed: {status.get('error', 'Unknown error')}")
                
                time.sleep(1)  # Wait before polling again
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Foocus server: {str(e)}")

def main():
    # Example usage
    client = FoocusClient()
    
    try:
        # Generate an image
        prompt = "A beautiful sunset over mountains, digital art style"
        negative_prompt = "blurry, low quality, distorted"
        
        print("Generating image...")
        image_paths = client.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            style_preset="None",
            image_number=1
        )
        
        print("Generated images saved at:")
        for path in image_paths:
            print(f"- {path}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 
