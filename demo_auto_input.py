import time
import webbrowser
import pyautogui

def type_text(text):
    for char in text:
        pyautogui.write(char)
        time.sleep(0.05)

def demo():
    print("충성! 코다리 부장입니다. 미스터리 채널 전략을 시연하겠습니다!")
    
    # 1. Open the app
    webbrowser.open("http://127.0.0.1:8501")
    time.sleep(5)  # Wait for page load
    
    # 2. Click sidebar to ensure focus (approximate coordinate, might need adjustment or manual focus)
    # Since we can't reliably know coordinates, we'll ask user to focus or use tab traversal.
    # Let's try tab traversal.
    
    # Assume focus starts at top.
    # Tab to Topic Input
    pyautogui.press('tab') 
    pyautogui.press('tab') 
    
    # 3. Enter Topic
    topic = "미스터리 미해결 사건 top 5"
    type_text(topic)
    time.sleep(1)
    pyautogui.press('tab') 
    
    # 4. Enter Target
    target = "2030 호기심 많은 남녀"
    type_text(target)
    time.sleep(1)
    pyautogui.press('tab') 
    
    # 5. Select Tone (Down arrow to select '진지하고 전문적인' or similar)
    pyautogui.press('down')
    pyautogui.press('enter')
    
    print("대표님! 입력이 완료되었습니다. 이제 '제목 뽑기' 버튼만 누르시면 됩니다!")

if __name__ == "__main__":
    # Give user time to switch to browser if needed, but webbrowser.open should handle it
    demo()
