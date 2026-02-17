import google.generativeai as genai
import json
from pathlib import Path
import os
import sys

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

def try_generate(model_name):
    print(f"[-] Trying {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("test")
        if response and response.text:
            print("SUCCESS!")
            return True
    except Exception as e:
        print(f"FAILED ({e})")
        return False

api_key = get_api_key()
if not api_key:
    # Fallback to env var if file not found
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("No API Key found.")
else:
    genai.configure(api_key=api_key)
    print("--- Listing and Testing ALL Models ---")
    found_model = None
    try:
        for m in genai.list_models():
            print(f"Found model listed: {m.name}")
            if 'generateContent' in m.supported_generation_methods:
                if try_generate(m.name):
                    found_model = m.name
                    break
    except Exception as e:
        print(f"Error listing models: {e}")

    if found_model:
        print(f"\n[!!!] WORKING MODEL FOUND: {found_model}")
        with open("working_model_final.txt", "w", encoding="utf-8") as f:
            f.write(found_model)
    else:
        print("\n[X] No working model found in the entire list.")
