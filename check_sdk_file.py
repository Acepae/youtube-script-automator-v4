
import google.generativeai as genai
import sys

def check_sdk():
    with open("sdk_check_result.txt", "w") as f:
        f.write(f"Version: {genai.__version__}\n")
        if hasattr(genai, "ImageGenerationModel"):
            f.write("SUCCESS: genai.ImageGenerationModel exists.\n")
        else:
            f.write("FAILURE: genai.ImageGenerationModel DOES NOT exist.\n")
        
        f.write(f"Top level genai dir: {dir(genai)}\n")

if __name__ == "__main__":
    check_sdk()
