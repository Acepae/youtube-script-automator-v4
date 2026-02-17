
import google.generativeai as genai
import sys

def check_sdk():
    try:
        with open("sdk_final_result.txt", "w") as f:
            f.write(f"Version: {genai.__version__}\n")
            if hasattr(genai, "ImageGenerationModel"):
                f.write("SUCCESS: genai.ImageGenerationModel exists.\n")
            else:
                f.write("FAILURE: genai.ImageGenerationModel DOES NOT exist.\n")
            
            # List commonly available attributes
            f.write(f"GenAI dir: {dir(genai)}\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sdk()
