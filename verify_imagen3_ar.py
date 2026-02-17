
import google.generativeai as genai
import os
import json
from PIL import Image
import io

def get_api_key():
    config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]
    except:
        return os.getenv("GEMINI_API_KEY")

def verify_imagen3():
    print("Testing Imagen 3.0 Generation 001 for 9:16...")
    try:
        model = genai.GenerativeModel("models/imagen-3.0-generate-001")
        response = model.generate_images(
            prompt="A tall skyscraper in Seoul, 9:16 aspect ratio",
            number_of_images=1,
            aspect_ratio="9:16"
        )
        if response.images:
            img = response.images[0]
            print(f"RESULT SIZE: {img.size}")
            if img.size[0] != img.size[1]:
                 print("SUCCESS: Non-square image generated.")
            else:
                 print("FAILURE: Square image generated.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    verify_imagen3()
