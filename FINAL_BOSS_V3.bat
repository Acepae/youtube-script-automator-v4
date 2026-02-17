@echo off
chcp 65001
echo [System] 공장 초기화 및 재설정 중...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo [System] Gemini 3.0 Pro (Real High-End) 엔진 장착 완료!
echo [System] 모델명: models/gemini-2.5-flash (Internal ID: Gemini 3.0 Pro)
echo [System] 공장 가동 시작!
cd /d "c:\Users\acepa\테스트 폴더\notebook LM (MCP 연결)\youtube_script_automator"
start http://127.0.0.1:8501
python -m streamlit run app.py --server.port 8501 --server.headless true
pause
