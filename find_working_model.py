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

def test_model(model_name):
    print(f"Testing {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        if response and response.text:
            print("SUCCESS!")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

api_key = get_api_key()
if not api_key:
    print("Failed to get API key.")
else:
    genai.configure(api_key=api_key)
    
    candidates = [
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro-001",
        "gemini-pro", 
        "gemini-1.0-pro",
        "models/gemini-1.5-pro",
        "models/gemini-pro"
    ]
    
    working_model = None
    for m in candidates:
        if test_model(m):
            working_model = m
            break
            
    if working_model:
        print(f"\n[FOUND] Working Model: {working_model}")
        with open("working_model.txt", "w", encoding="utf-8") as f:
            f.write(working_model)
    else:
        print("\n[ERROR] No working model found in candidates.")
