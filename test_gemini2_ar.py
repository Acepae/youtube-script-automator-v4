
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

def test_config():
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    prompt = "A futuristic city in Korea, vertical aspect ratio"
    print(f"Testing Gemini 2.0 Flash Exp with aspectRatio config")
    
    configs_to_test = [
        {"aspectRatio": "9:16"},
        {"aspect_ratio": "9:16"},
        {"media_resolution": "9:16"}
    ]
    
    for config in configs_to_test:
        print(f"\n--- Config: {config} ---")
        try:
            model = genai.GenerativeModel("models/gemini-2.0-flash-exp-image-generation")
            # Some versions might require types.GenerationConfig
            response = model.generate_content(prompt, generation_config=config)
            
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image = Image.open(io.BytesIO(part.inline_data.data))
                        print(f"SUCCESS: Image Size: {image.size}")
                    if hasattr(part, 'text') and part.text:
                        print(f"Text: {part.text[:50]}")
            else:
                print("No parts.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_config()
