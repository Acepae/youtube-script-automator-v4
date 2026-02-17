
import script_generator as sg
import os
import json
import google.generativeai as genai

def setup_env():
    config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            os.environ["GEMINI_API_KEY"] = config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]
            return True
    except:
        return False

def test_prompt_localization():
    print("Testing create_image_prompt for Korean context...")
    
    # Generic input that doesn't explicitly mention Korea
    script_segment = "A busy city street in the morning. People are rushing to work with coffee cups."
    style = "Cinematic, Realistic"
    
    prompt = sg.create_image_prompt(script_segment, style)
    
    print("\n--- Generated Prompt ---")
    print(prompt)
    print("------------------------")
    
    keywords = ["Korea", "Seoul", "Asian", "Hangul"]
    found = [k for k in keywords if k.lower() in prompt.lower()]
    
    if found:
        print(f"SUCCESS: Found localization keywords: {found}")
    else:
        print("WARNING: No obvious localization keywords found. Check the prompt manually.")

if __name__ == "__main__":
    if setup_env():
        test_prompt_localization()
    else:
        print("Failed to setup auth.")
