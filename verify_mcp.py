
import json
import os

def test_mcp_connection():
    config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
    print(f"Checking MCP Config at: {config_path}")
    
    if not os.path.exists(config_path):
        print("❌ File NOT FOUND")
        return
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Traverse the JSON structure
            gemini_config = config.get("mcpServers", {}).get("gemini", {})
            env_vars = gemini_config.get("env", {})
            api_key = env_vars.get("GEMINI_API_KEY")
            
            if api_key:
                masked_key = api_key[:5] + "..." + api_key[-5:]
                print(f"✅ SUCCESS: Found Gemini API Key in MCP Config!")
                print(f"   Key: {masked_key}")
            else:
                print("❌ FAILED: 'GEMINI_API_KEY' not found in config json.")
                print(f"   Structure found: {gemini_config.keys()}")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_mcp_connection()
