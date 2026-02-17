@echo off
chcp 65001
echo [System] 공장 초기화 중... (모든 Python 프로세스 종료)
taskkill /F /IM python.exe
timeout /t 2 >nul
echo.
echo [System] 공장 재가동 시작! (서버 실행)
echo [System] 잠시만 기다려주세요...
cd /d "c:\Users\acepa\테스트 폴더\notebook LM (MCP 연결)\youtube_script_automator"
python run_server.py
pause
