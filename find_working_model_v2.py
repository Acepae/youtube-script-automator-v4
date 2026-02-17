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
        return None

def test_model(model_name, log_file):
    msg = f"Testing {model_name}..."
    print(msg)
    log_file.write(msg + "\n")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        if response and response.text:
            success_msg = f"SUCCESS: {model_name}\n"
            print(success_msg)
            log_file.write(success_msg)
            return True
    except Exception as e:
        fail_msg = f"FAILED: {model_name} - {str(e)}\n"
        print(fail_msg)
        log_file.write(fail_msg)
        return False

api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)
    
    candidates = [
        "gemini-1.5-pro",
        "models/gemini-1.5-pro",
        "gemini-pro",
        "models/gemini-pro",
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-2.0-flash-exp",
        "models/gemini-2.0-flash-exp"
    ]
    
    with open("model_test_log.txt", "w", encoding="utf-8") as log:
        for m in candidates:
            if test_model(m, log):
                break
