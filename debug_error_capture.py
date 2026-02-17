
import google.generativeai as genai
import os
import json
import traceback

def get_api_key():
    config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]
    except:
        return os.getenv("GEMINI_API_KEY")

def log_error(msg):
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

if __name__ == "__main__":
    if os.path.exists("error_log.txt"): os.remove("error_log.txt")
    
    api_key = get_api_key()
    if not api_key:
        log_error("No API Key")
        exit()

    genai.configure(api_key=api_key)
    prompt = "A cute cat, 2k resolution, aspect ratio 16:9"

    # Test 1: Gemini 2.0 Flash Exp Image Gen
    model_name = "models/gemini-2.0-flash-exp-image-generation"
    log_error(f"--- Testing {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        log_error(f"Success? Parts: {len(response.parts) if response.parts else 0}")
    except Exception:
        log_error(traceback.format_exc())

    # Test 2: Gemini 2.0 Flash (Standard)
    model_name = "models/gemini-2.0-flash"
    log_error(f"--- Testing {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        log_error(f"Success? Parts: {len(response.parts) if response.parts else 0}")
    except Exception:
        log_error(traceback.format_exc())
