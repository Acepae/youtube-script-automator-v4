@echo off
cd /d "c:\Users\acepa\테스트 폴더\notebook LM (MCP 연결)\youtube_script_automator"
echo [DEBUG MODE] Installing requirements...
pip install -r requirements.txt
echo [DEBUG MODE] Starting Streamlit...
python -m streamlit run app.py --server.port 8501
pause
