
import script_generator as sg
import os
import json
import google.generativeai as genai

# Setup auth manually for the script context if needed, though sg.configure_genai might handle it.
# We'll just rely on sg.configure_genai()
# But we need to ensure API key is set in env or config.

def test_generation():
    print("Testing generate_image_from_prompt...")
    
    complex_prompt = "A futuristic laboratory with sleek white surfaces, blue neon lighting, and a holographic display showing a DNA double helix. A scientist in a white coat is examining data. High detailed, cinematic lighting, 8k resolution."
    aspect_ratio = "16:9"
    
    img = sg.generate_image_from_prompt(complex_prompt, aspect_ratio)
    
    if img:
        print("SUCCESS: Image generated!")
        img.save("test_output.png")
    else:
        print("FAILURE: No image returned.")

if __name__ == "__main__":
    # Ensure key is available
    config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            os.environ["GEMINI_API_KEY"] = config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]
    except:
        pass
        
    test_generation()
