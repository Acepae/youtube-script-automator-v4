@echo off
cd /d "c:\Users\acepa\테스트 폴더\notebook LM (MCP 연결)\youtube_script_automator"
pip install -r requirements.txt
python -m streamlit run app.py --server.port 8501 --server.headless true
pause
