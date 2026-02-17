
import requests
import json
import os
import base64
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

def test_gemini_rest(model_name, ar_config):
    api_key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    
    # Try injecting aspect ratio params into generationConfig
    # We test different keys: aspectRatio, aspect_ratio, mediaResolution
    data = {
        "contents": [
            {"parts": [{"text": "Generate a vertical image of Seoul, 9:16 aspect ratio"}]}
        ],
        "generationConfig": ar_config
    }
    
    print(f"\n--- Testing {model_name} with config {ar_config} ---")
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            # print(json.dumps(result, indent=2))
            
            # Check for inline data
            if "candidates" in result and result["candidates"]:
                parts = result["candidates"][0]["content"]["parts"]
                for part in parts:
                    if "inlineData" in part:
                        b64 = part["inlineData"]["data"]
                        img = Image.open(io.BytesIO(base64.b64decode(b64)))
                        print(f"SUCCESS: Image Size: {img.size}")
                        return
            print("No image in response.")
        else:
            print(f"Error ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test valid model
    model = "gemini-2.0-flash-exp" # generic multimodal
    # model = "gemini-2.5-flash-image" # fails?
    
    # configs to test
    configs = [
        {"aspectRatio": "9:16"}, 
        {"mediaResolution": "9:16"},
        {"sampleCount": 1} # control
    ]
    
    # We try 'gemini-2.0-flash-exp' first as it is multimodal
    for c in configs:
        test_gemini_rest("gemini-2.0-flash-exp", c)
        
    # We also try the dedicated image model via generateContent?
    # Some users reported gemini-2.0-flash-exp supports image generation
