
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

def log(msg):
    with open("gen_debug.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

if __name__ == "__main__":
    if os.path.exists("gen_debug.txt"): os.remove("gen_debug.txt")
    
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    prompt = "A cute cat, 2k resolution, aspect ratio 16:9"
    model_name = "models/gemini-2.0-flash-exp-image-generation"
    
    log(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        log(f"Response Parts: {len(response.parts)}")
        for i, part in enumerate(response.parts):
            log(f"Part {i}:")
            if hasattr(part, 'text') and part.text:
                log(f"  Type: Text")
                log(f"  Content: {part.text[:100]}...")
            if hasattr(part, 'inline_data') and part.inline_data:
                log(f"  Type: Inline Data")
                log(f"  MimeType: {part.inline_data.mime_type}")
                log(f"  Data Length: {len(part.inline_data.data)}")
            if hasattr(part, 'function_call') and part.function_call:
                 log(f"  Type: Function Call")
                 
    except Exception as e:
        log(f"Error: {e}")
