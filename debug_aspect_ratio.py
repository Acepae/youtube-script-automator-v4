
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

def test_model_ar(model_name, prompt, config=None):
    print(f"\n--- Testing Model: {model_name} ---")
    print(f"Prompt: {prompt}")
    if config: print(f"Config: {config}")
    
    try:
        model = genai.GenerativeModel(model_name)
        
        response = None
        if config:
            # Need to wrap config in types.GenerationConfig if passing dict?
            # Or pass as kwargs? generate_content(prompt, generation_config=...)
            response = model.generate_content(prompt, generation_config=config)
        else:
            response = model.generate_content(prompt)
            
        if response.parts:
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image = Image.open(io.BytesIO(part.inline_data.data))
                    print(f"SUCCESS: Image generated. Size: {image.size}")
                    return
                if hasattr(part, 'text') and part.text:
                    print(f"Text Response: {part.text[:100]}...")
        else:
            print("No parts.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    prompt = "A futuristic city skyline in South Korea, highly detailed, cinematic lighting"
    
    # Test 1: Gemini 2.0 Flash Exp Image Gen (Safe Prompt)
    # This model *should* support prompt-based AR
    test_model_ar("models/gemini-2.0-flash-exp-image-generation", f"{prompt}, aspect ratio 9:16")
    
    # Test 2: Gemini 2.5 Flash Image with explicit config (CamelCase)
    # Some older docs suggest 'aspectRatio'
    test_model_ar("models/gemini-2.5-flash-image", prompt, {"aspectRatio": "9:16"})
    
    # Test 3: Gemini 2.5 Flash Image with snake_case config
    test_model_ar("models/gemini-2.5-flash-image", prompt, {"aspect_ratio": "9:16"})
    
    # Test 4: Gemini 2.5 Flash Image with 'sampleCount' (to see if config is respected at all)
    test_model_ar("models/gemini-2.5-flash-image", prompt, {"sampleCount": 1})
