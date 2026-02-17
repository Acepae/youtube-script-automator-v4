@echo off
cd /d "c:\Users\acepa\테스트 폴더\notebook LM (MCP 연결)\youtube_script_automator"
echo [System] Installing requirements...
pip install -r requirements.txt
echo [System] Starting Streamlit App...
echo [System] If the browser does not open automatically, please visit http://127.0.0.1:8501
start "" "http://127.0.0.1:8501"
python -m streamlit run app_v2.py --server.port 8501
pause
