
import google.generativeai as genai

try:
    print(f"ImageGenerationModel exists: {'ImageGenerationModel' in dir(genai)}")
except:
    print("Error checking dir(genai)")
