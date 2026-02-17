$path = "c:\Users\acepa\테스트 폴더\notebook LM (MCP 연결)\youtube_script_automator"
Set-Location -Path $path
Write-Host "[System] Installing requirements..."
pip install -r requirements.txt
Write-Host "[System] Starting Streamlit App (Port 8503)..."
Start-Process "http://127.0.0.1:8503"
python -m streamlit run app.py --server.port 8503 --server.headless true
