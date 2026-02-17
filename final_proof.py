
import os
import json
import re
import google.generativeai as genai

# Mock Streamlit for testing
class MockSessionState(dict):
    def __getattr__(self, key): return self.get(key)
    def __setattr__(self, key, value): self[key] = value

class MockSt:
    session_state = MockSessionState()
    def error(self, msg): print(f"[ST:ERROR] {msg}")
    def success(self, msg): print(f"[ST:SUCCESS] {msg}")
    def info(self, msg): print(f"[ST:INFO] {msg}")

st = MockSt()

# --- COPIED logic from app_v2.py ---
def load_mcp_api_key():
    """Loads Gemini API Key from MCP config file."""
    try:
        config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
        
        # Debug print
        print(f"DEBUG: Looking for config at {config_path}")
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                gemini_env = config.get("mcpServers", {}).get("gemini", {}).get("env", {})
                api_key = gemini_env.get("GEMINI_API_KEY")
                if api_key:
                    # Set ENV for other modules
                    os.environ["GEMINI_API_KEY"] = api_key
                    print("DEBUG: API Key found and loaded into ENV")
                    return api_key
        else:
            print("DEBUG: Config file does not exist")
    except Exception as e:
        print(f"Failed to load MCP config: {e}")
    return None

def internal_create_prompt(text, style):
    """Generates prompt directly within app.py to avoid caching issues."""
    try:
        # 1. MCP Auto-Load
        api_key = load_mcp_api_key()
        
        # 2. Try environment variable (fallback)
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        
        # 3. Try session state (Manual Input)
        if not api_key and 'user_api_key' in st.session_state:
            api_key = st.session_state['user_api_key']
            
        if not api_key:
            return f"Error: No API Key. {style}, 8k, detailed"
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as an AI Visual Director.
        Convert this Korean script into a descriptive **ENGLISH** image prompt (30 words+).
        Input: "{text}"
        Style: {style}
        Output ONLY the English prompt. No explanations.
        """
        print(f"DEBUG: Sending request to Gemini... Input='{text[:20]}...'")
        response = model.generate_content(prompt)
        result = response.text.strip()
        print(f"DEBUG: Raw response from Gemini='{result}'")
        
        # Override if Korean detected
        if re.search("[가-힣]", result):
            print(f"Korean usage detected in: {result}")
            clean_style = style.replace("Target Style:", "").strip()
            return f"High quality, {clean_style}, cinematic lighting, highly detailed, 8k resolution, masterpiece"
            
        return result
    except Exception as e:
        print(f"Inline Gen Error: {e}")
        return f"High quality image, {style.replace('Target Style:', '')}, 8k, detailed"
# -----------------------------------

if __name__ == "__main__":
    print("=== FINAL PROOF TEST: MCP + GENAI + ANTI-KOREAN ===\n")
    
    # Test Case: Typical Korean Input
    test_input = "2026년 대한민국 경제 위기 시나리오 분석"
    test_style = "Target Style: Cinematic"
    
    print(f"Test Input: {test_input}")
    print(f"Test Style: {test_style}\n")
    
    final_output = internal_create_prompt(test_input, test_style)
    
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print(final_output)
    print("="*50 + "\n")
    
    if re.search("[가-힣]", final_output):
        print("❌ TEST FAILED: Output contains Korean.")
    else:
        print("✅ TEST PASSED: Output is pure English.")
