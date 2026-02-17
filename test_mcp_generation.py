
import json
import os
import google.generativeai as genai

def test_generation():
    print("=== MCP Key Generation Test ===")
    
    # 1. Load Key
    config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
    if not os.path.exists(config_path):
        print("❌ Config file not found")
        return

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get("mcpServers", {}).get("gemini", {}).get("env", {}).get("GEMINI_API_KEY")
            
        if not api_key:
            print("❌ No API Key in config")
            return
            
        print(f"✅ Key Found: {api_key[:5]}...")
        
        # 2. Configure GenAI
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 3. Try Generation
        print("🚀 Sending request to Gemini...")
        response = model.generate_content("Say 'Hello' in English only.")
        
        print(f"🎉 Response: {response.text}")
        print("✅ Generation SUCCESS!")
        
    except Exception as e:
        print(f"❌ Generation FAILED: {e}")

if __name__ == "__main__":
    test_generation()
