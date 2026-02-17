import google.generativeai as genai
import json
import os

def get_api_key():
    config_path = "C:/Users/acepa/.gemini/antigravity/mcp_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]
    except Exception as e:
        print(f"Error: {e}")
        return None

key = get_api_key()
if key:
    genai.configure(api_key=key)
    print("Listing models...")
    with open("verified_models.txt", "w", encoding="utf-8") as outfile:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
                outfile.write(m.name + "\n")
else:
    print("No key found")
