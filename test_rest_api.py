
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

def test_rest():
    api_key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    data = {
        "instances": [
            {"prompt": "A tall skyscraper in Seoul, 9:16 aspect ratio"}
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "9:16"
        }
    }
    
    print("Sending REST request to Imagen 3...")
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            # print(json.dumps(result, indent=2))
            
            # Extract image
            # structure: predictions: [{ bytesBase64Encoded: ... }]
            if "predictions" in result:
                b64_data = result["predictions"][0]["bytesBase64Encoded"]
                image_data = base64.b64decode(b64_data)
                image = Image.open(io.BytesIO(image_data))
                print(f"SUCCESS: Image generated. Size: {image.size}")
                if image.size[0] != image.size[1]:
                    print("VERIFIED: Non-square (9:16) aspect ratio.")
                else:
                    print("WARNING: Square image.")
            else:
                 print("No predictions found.")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_rest()
