
import re
import os

# Mocking the internal function logic from app_v2.py
def mock_internal_create_prompt(text, style):
    print(f"[TEST] Input Text: {text}")
    print(f"[TEST] Input Style: {style}")
    
    # 1. Simulating a "Bad" Model Response (Korean)
    bad_response = f"파싱된 주제: {text}에 대한 고품질 이미지"
    print(f"[TEST] Model Raw Output (Simulated): {bad_response}")
    
    # 2. Applying Anti-Korean Logic
    result = bad_response.strip()
    
    if re.search("[가-힣]", result):
        print("🚨 [DETECTED] Korean/Bad characters detected!")
        clean_style = style.replace("Target Style:", "").strip()
        # Fallback Logic
        forced_english = f"High quality, {clean_style}, cinematic lighting, highly detailed, 8k resolution, masterpiece"
        print(f"✅ [FIXED] Force-converted to English: {forced_english}")
        return forced_english
    
    print("❌ [FAIL] Logic failed to detect Korean")
    return result

if __name__ == "__main__":
    print("=== Anti-Korean Logic Self-Test ===")
    
    test_inputs = [
        ("2026년 대한민국 환율 위기", "Cinematic"),
        ("맛있는 김치찌개 끓이는 법", "Vlog"),
        ("Unity 튜토리얼", "Documentary")
    ]
    
    for txt, sty in test_inputs:
        print("\n--- Case Start ---")
        final_output = mock_internal_create_prompt(txt, sty)
        
        if re.search("[가-힣]", final_output):
             print(f"FAILED: Output contained Korean: {final_output}")
        else:
             print(f"SUCCESS: Output is pure English: {final_output}")
             
    print("\n=== Test Complete ===")
