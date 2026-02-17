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

api_key = get_api_key()
if not api_key:
    print("Failed to get API key.")
else:
    genai.configure(api_key=api_key)
    print("--- Checking Specific Models ---")
    target_models = ['gemini-1.5-pro', 'gemini-1.5-pro-001', 'gemini-1.5-pro-latest', 'gemini-pro', 'gemini-1.0-pro']
    found = False
    all_models = []
    try:
        for m in genai.list_models():
            all_models.append(m.name)
            for target in target_models:
                if target in m.name:
                    print(f"FOUND MATCH: {m.name}")
                    found = True
    except Exception as e:
        print(f"Error listing models: {e}")
    
    if not found:
        print("No standard Pro models found. Printing all available:")
        for m_name in all_models:
            print(m_name)
