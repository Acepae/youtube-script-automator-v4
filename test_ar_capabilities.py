
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

def test_generation(model_name, prompt, config=None, test_name=""):
    print(f"\n--- TEST: {test_name} [{model_name}] ---")
    print(f"Prompt: {prompt}")
    if config: print(f"Config: {config}")
    
    try:
        model = genai.GenerativeModel(model_name)
        
        # Check if model supports generate_images (Imagen legacy) or generate_content (Gemini)
        # We try generate_content first as it's the modern standard
        try:
            if config:
                response = model.generate_content(prompt, generation_config=config)
            else:
                response = model.generate_content(prompt)
                
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image = Image.open(io.BytesIO(part.inline_data.data))
                        print(f"SUCCESS (Content): Image generated. Size: {image.size}")
                        return image.size
                    if hasattr(part, 'text') and part.text:
                         print(f"Text Response: {part.text[:50]}...")
            else:
                print("No parts in response.")
                
        except Exception as e_content:
            print(f"generate_content failed: {e_content}")
            
            # Fallback to generate_images (for Imagen specific models)
            try:
                print("Trying generate_images method...")
                # legacy args mapping
                ar = config.get("aspect_ratio") if config else None
                response = model.generate_images(prompt=prompt, aspect_ratio=ar)
                image = response.images[0]
                print(f"SUCCESS (Images): Image generated. Size: {image.size}")
                return image.size
            except Exception as e_img:
                print(f"generate_images failed: {e_img}")

    except Exception as e:
        print(f"Model init failed: {e}")
    return None

if __name__ == "__main__":
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    prompt = "A futuristic city in Korea, cyberpunk style"
    
    # 1. Gemini 2.0 Flash Exp - Prompt only
    test_generation("models/gemini-2.0-flash-exp-image-generation", f"{prompt}, aspect ratio 9:16", test_name="2.0-Exp Prompt AR")

    # 2. Gemini 2.0 Flash Exp - Config snake_case (if supported)
    test_generation("models/gemini-2.0-flash-exp-image-generation", prompt, {"aspect_ratio": "9:16"}, test_name="2.0-Exp Config snake")

    # 3. Gemini 2.0 Flash Exp - Config camelCase
    test_generation("models/gemini-2.0-flash-exp-image-generation", prompt, {"aspectRatio": "9:16"}, test_name="2.0-Exp Config camel")
    
    # 4. Imagen 3 (if accessible)
    test_generation("models/imagen-3.0-generate-001", prompt, {"aspect_ratio": "9:16"}, test_name="Imagen 3 Config")
    
    # 5. Gemini 2.5 Flash Image - Prompt
    test_generation("models/gemini-2.5-flash-image", f"{prompt} --ar 9:16", test_name="2.5-Flash Prompt AR")
