
import google.generativeai as genai
import os
import json

def check_sdk():
    print("Checking GenAI SDK...")
    print(f"Version: {genai.__version__}")
    if hasattr(genai, "ImageGenerationModel"):
        print("SUCCESS: genai.ImageGenerationModel exists.")
    else:
        print("FAILURE: genai.ImageGenerationModel DOES NOT exist.")
    
    # Check what GenerativeModel has
    model = genai.GenerativeModel("gemini-1.5-flash")
    print(f"GenerativeModel methods: {[m for m in dir(model) if 'generate' in m]}")

if __name__ == "__main__":
    check_sdk()
