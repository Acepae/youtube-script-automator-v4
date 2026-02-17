import script_generator as sg
import os

print("=== DEBUG START ===")

# 1. Check Auth
print("Checking Auth...")
auth_success = sg.configure_genai()
print(f"Auth Success: {auth_success}")

# 2. Test Prompt Generation
test_script = "안녕하세요, 오늘은 맛있는 요리를 해볼게요."
test_style = "Target Style: Cinematic"

print(f"\nTesting create_image_prompt with:\nScript: {test_script}\nStyle: {test_style}")

try:
    result = sg.create_image_prompt(test_script, test_style)
    print(f"\n[RESULT]:\n{result}")
except Exception as e:
    print(f"\n[ERROR]:\n{e}")

print("=== DEBUG END ===")
