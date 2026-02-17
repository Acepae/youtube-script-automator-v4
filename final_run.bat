@echo off
chcp 65001
cd /d "c:\Users\acepa\테스트 폴더\notebook LM (MCP 연결)\youtube_script_automator"
echo [System] Installing requirements...
pip install -r requirements.txt
echo [System] Starting Streamlit App (Port 8502)...
start "" "http://127.0.0.1:8502"
python -m streamlit run app.py --server.port 8502 --server.headless true
pause
