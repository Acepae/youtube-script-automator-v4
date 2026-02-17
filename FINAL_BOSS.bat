@echo off
chcp 65001
echo [System] 공장 초기화 중... (모든 Python 프로세스 종료)
taskkill /F /IM python.exe
timeout /t 2 >nul

echo [System] Streamlit 설정 초기화...
mkdir %USERPROFILE%\.streamlit 2>nul
echo [general] > %USERPROFILE%\.streamlit\credentials.toml
echo email = "" >> %USERPROFILE%\.streamlit\credentials.toml

echo.
echo [System] 최종 공장 가동 시작! (포트 8501)
cd /d "c:\Users\acepa\테스트 폴더\notebook LM (MCP 연결)\youtube_script_automator"
python -m streamlit run app.py --server.port 8501 --server.headless true
pause
