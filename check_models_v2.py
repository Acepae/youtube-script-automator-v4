import google.generativeai as genai
import json
from pathlib import Path
import os
import sys

# Set encoding to utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

def get_api_key():
    config_path = Path("C:/Users/acepa/.gemini/antigravity/mcp_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]
    except Exception as e:
        print(f"Error reading API key: {e}")
        return None

api_key = get_api_key()
if not api_key:
    print("Failed to get API key.")
else:
    genai.configure(api_key=api_key)
    print("--- Available Models ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model Name: {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
    print("--- End of List ---")
