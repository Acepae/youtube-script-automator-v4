
import google.generativeai as genai
import os
import json

def get_api_key():
    config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]
    except:
        return os.getenv("GEMINI_API_KEY")

api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)
    with open("models_out.txt", "w", encoding="utf-8") as f:
        f.write("Listing models...\n")
        for m in genai.list_models():
            f.write(f"Name: {m.name}\n")
            f.write(f"Supported methods: {m.supported_generation_methods}\n")
else:
    with open("models_out.txt", "w", encoding="utf-8") as f:
        f.write("No API Key\n")
