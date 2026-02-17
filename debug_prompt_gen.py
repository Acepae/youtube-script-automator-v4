import script_generator as sg
import google.generativeai as genai
import os

print("Testing create_image_prompt...")

# 1. Test Auth
print("1. Configuring GenAI...")
if sg.configure_genai():
    print("   Auth OK")
else:
    print("   Auth FAILED")

# 2. Test Prompt Gen
print("2. Generating Prompt...")
dummy_script = "진행자: 오늘은 맛있는 사과를 먹어봅시다."
dummy_style = "Target Style: Cinematic"

try:
    result = sg.create_image_prompt(dummy_script, dummy_style)
    print(f"   Result: '{result}'")
except Exception as e:
    print(f"   Exception: {e}")

print("Done.")
