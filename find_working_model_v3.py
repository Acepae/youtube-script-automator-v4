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
        print(f"Error reading config: {e}")
        return None

key = get_api_key()
if not key:
    print("No API Key found.")
    exit()

genai.configure(api_key=key)

candidates = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-1.5-pro-001",
    "gemini-pro",
    "gemini-1.0-pro"
]

print("Testing models...")
working_model = None

for model_name in candidates:
    print(f"Testing {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        if response.text:
            print("SUCCESS")
            working_model = model_name
            break
    except Exception as e:
        print(f"FAILED: {e}")

if working_model:
    print(f"\nFOUND WORKING MODEL: {working_model}")
    with open("working_model.txt", "w", encoding="utf-8") as f:
        f.write(working_model)
else:
    print("\nNO WORKING MODELS FOUND.")
