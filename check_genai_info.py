
import google.generativeai as genai
import sys

print(f"Python version: {sys.version}")
try:
    print(f"GenAI version: {genai.__version__}")
except:
    print("GenAI version not found")

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("GenerativeModel capabilities:")
    for d in dir(model):
        if 'generate' in d:
            print(f" - {d}")
except Exception as e:
    print(f"Error inspecting model: {e}")
