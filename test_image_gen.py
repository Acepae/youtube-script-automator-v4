import google.generativeai as genai
import json
from pathlib import Path

def get_api_key():
    config_path = Path("C:/Users/acepa/.gemini/antigravity/mcp_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        return config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]

api_key = get_api_key()
genai.configure(api_key=api_key)

# Test with gemini-3-pro-image-preview (listed as Gemini 3 Pro Image Preview)
# or nano-banana-pro-preview
model_name = 'gemini-3-pro-image-preview'
print(f"Testing image generation with {model_name}...")

try:
    model = genai.GenerativeModel(model_name)
    # Most likely this model takes a text prompt and returns an image object
    # If the library doesn't support it directly, this might fail.
    response = model.generate_content("A beautiful sunset over the digital city")
    print("Response received!")
    # Check if there's image data in the response
    print(response)
except Exception as e:
    print(f"Error: {e}")
