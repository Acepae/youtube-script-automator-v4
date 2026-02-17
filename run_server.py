import os
import sys
import subprocess
import webbrowser
import time

def main():
    # Set the working directory to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"[System] Working Directory: {script_dir}")

    # Install requirements if needed (skipping for speed if already done, but safer to try)
    # subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--server.address", "127.0.0.1"
    ]

    print("[System] Starting Streamlit Server...")
    process = subprocess.Popen(cmd)

    # Give it a moment to start
    time.sleep(3)

    # Open browser
    url = "http://127.0.0.1:8501"
    print(f"[System] Opening browser at {url}")
    webbrowser.open(url)

    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n[System] Stopping server...")
        process.terminate()

if __name__ == "__main__":
    main()
