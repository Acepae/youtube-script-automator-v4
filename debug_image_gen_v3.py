# Test script for available models
import google.generativeai as genai
import json
import sys

# Load API Key
config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        api_key = config.get("mcpServers", {}).get("gemini", {}).get("env", {}).get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error loading key: {e}")

def test_model(model_name, prompt):
    with open("gen_test_result.txt", "a") as f:
        f.write(f"\n--- Testing {model_name} ---\n")
    try:
        model = genai.GenerativeModel(model_name)
        
        print(f"Generating content with '{prompt}'...")
        response = model.generate_content(prompt)
        print("Response received.")
        
        with open("gen_test_result.txt", "a") as f:
            f.write("Response received.\n")
            if hasattr(response, 'parts'):
                f.write(f"Parts count: {len(response.parts)}\n")
                if len(response.parts) > 0:
                    part = response.parts[0]
                    f.write(f"Part dir: {dir(part)}\n")
                    # Try accessing common fields safely
                    try:
                        f.write(f"Part text: {part.text}\n")
                    except:
                        f.write("Part has no text\n")
                    
                    try:
                        f.write(f"Part inline_data: {part.inline_data}\n")
                    except:
                        f.write("Part has no inline_data\n")
            else:
                f.write(f"Response text: {response.text[:100]}...\n")
            
    except Exception as e:
        with open("gen_test_result.txt", "a") as f:
            f.write(f"FAILED: {e}\n")

# Test 1: Imagen 4
test_model('models/imagen-4.0-generate-001', 'A futuristic city, high quality')

# Test 2: Gemini 3 Image Preview
test_model('models/gemini-3-pro-image-preview', 'A futuristic city, high quality')

# Test 3: Gemini 2.0 Flash Image Gen
test_model('models/gemini-2.0-flash-exp-image-generation', 'generate an image of a futuristic city')
