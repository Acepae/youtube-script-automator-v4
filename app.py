import streamlit as st
import script_generator as sg
import json
import os
from PIL import Image

st.set_page_config(page_title="유튜브 대본 공장 (멀티모달 + 이미지)", page_icon="🏭", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background: linear-gradient(45deg, #FF4B4B, #FF8F8F); color: white; border: none; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); background: linear-gradient(45deg, #FF8F8F, #FF4B4B); }
    .stTextArea>div>div>textarea { background-color: #1e2129; color: #ffffff; border-radius: 10px; }
    .stTextInput>div>div>input { background-color: #1e2129; color: #ffffff; border-radius: 10px; }
    .stSelectbox>div>div>div { background-color: #1e2129; border-radius: 10px; }
    .part-box { background-color: #262730; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #41444e; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏭 유튜브 스토리텔링 대본 공장 (v2.1)")
st.markdown("### 주제와 참고 자료를 넣으면, '일관된 스타일'의 이미지까지 함께 생성합니다.")

# Session State
if 'step' not in st.session_state: st.session_state.step = 1
if 'titles' not in st.session_state: st.session_state.titles = ""
if 'selected_title' not in st.session_state: st.session_state.selected_title = ""
if 'outline' not in st.session_state: st.session_state.outline = ""
if 'script_data' not in st.session_state: st.session_state.script_data = {} # Structure: {key: {'text': ..., 'prompt': ..., 'image': ...}}
if 'script_text_raw' not in st.session_state: st.session_state.script_text_raw = ""
if 'uploaded_images' not in st.session_state: st.session_state.uploaded_images = []

# Sidebar
with st.sidebar:
    st.header("⚙️ 설정")
    topic = st.text_input("영상 주제", value="", placeholder="주제를 입력해 주세요", key="input_topic_fixed")
    target = st.text_input("타겟 시청자", value="", placeholder="타겟을 입력해 주세요", key="input_target_fixed")
    
    st.markdown("---")
    st.subheader("🎨 이미지 설정")
    image_style_ui = st.selectbox("이미지 스타일", [
        "선택 안 함 (AI 자율)", 
        "실사 (Realistic Photo)", 
        "일본 에니매이션 (Anime)", 
        "3D 에니매이션 (Pixar Style)", 
        "영화 스틸컷 (Cinematic)", 
        "다큐멘터리 (Documentary)", 
        "브이로그 (Vlog)", 
        "빈티지 필름 (Vintage)", 
        "영화 같은 (Film Look)", 
        "게임 스타일 (Game Art)"
    ], index=4)
    
    aspect_ratio_ui = st.selectbox("이미지 비율", [
        "16:9 (유튜브 기본)", 
        "9:16 (쇼츠)", 
        "1:1 (정방형)", 
        "3:4 (인물)", 
        "4:3 (클래식)"
    ], index=0)

    # 파라미터 정제
    img_style_val = image_style_ui.split('(')[1].replace(')', '') if '(' in image_style_ui else image_style_ui
    if "선택 안 함" in image_style_ui: img_style_val = None
    
    aspect_ratio_val = aspect_ratio_ui.split(' ')[0] # "16:9", "9:16" 추출

    st.markdown("---")
    st.subheader("📏 길이 조절")
    intro_count = st.selectbox("인트로 파트 수", options=[1, 2, 3, 4, 5], index=0)
    body_count = st.selectbox("본문 파트 수", options=[i for i in range(1, 16)], index=9)
    # Length options
    length_options = [f"{i}분" for i in range(1, 6)] + [f"{i}분" for i in range(10, 91, 10)]
    idx_10min = length_options.index("10분") if "10분" in length_options else 5
    video_length = st.selectbox("예상 영상 길이", options=length_options, index=idx_10min)
    content_style = st.selectbox("콘텐츠 스타일", ["정보 전달/리뷰", "다큐멘터리/스토리텔링", "튜토리얼/강의", "동기부여/에세이"], index=1)

# Main
st.markdown("---")
col_file, col_text = st.columns(2)
uploaded_files = []
file_text_content = ""
image_objects = []

with col_file:
    st.subheader("📂 자료/이미지 업로드")
    uploaded_files = st.file_uploader("파일 선택 (TXT, JPG, PNG)", type=["txt", "pdf", "jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    if uploaded_files:
        for f in uploaded_files:
            try:
                if f.type.startswith("image"):
                    img = Image.open(f)
                    image_objects.append(img)
                    st.image(img, caption=f"참고 이미지: {f.name}", width=150)
                elif f.type == "text/plain":
                    text = f.read().decode("utf-8")
                    file_text_content += f"\n[File: {f.name}]\n{text}\n"
            except Exception as e:
                st.error(f"Error ({f.name}): {e}")

with col_text:
    st.subheader("✂️ 텍스트 입력")
    manual_text = st.text_area("텍스트 자료 붙여넣기", height=200, placeholder="내용 입력...")

combined_source = (file_text_content + "\n\n" + manual_text).strip()

st.markdown("---")
if st.button("🚀 멀티모달 대본 & 이미지 생성 시작"):
    if not topic:
        st.error("주제를 입력해 주세요!")
    else:
        st.session_state.step = 100
        st.session_state.titles = ""
        st.session_state.outline = ""
        st.session_state.script_data = {}
        st.session_state.script_text_raw = ""
        st.session_state.uploaded_images = image_objects

def parse_script_with_prompts(full_text):
    import re
    data = {}
    current_key = None
    
    lines = full_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 1. Image Prompt Detection (Inline or Start)
        # Regex to find [Image Prompt]: (case insensitive, optional stars, optional brackets)
        # Matches: [Image Prompt]:, **[Image Prompt]:**, Image Prompt:, etc.
        prompt_match = re.search(r'(\*\*|\[)?\s*Image Prompt\s*(\*\*|\])?\s*:', line, re.IGNORECASE)
        
        if prompt_match:
            # If found, split line
            start_idx = prompt_match.start()
            end_idx = prompt_match.end()
            
            text_part = line[:start_idx].strip()
            prompt_part = line[end_idx:].strip()
            
            if current_key:
                if text_part:
                    data[current_key]['text'] += " " + text_part
                
                # If prompt already exists, append (multiline prompt case)
                if data[current_key]['prompt']:
                    data[current_key]['prompt'] += " " + prompt_part
                else:
                    data[current_key]['prompt'] = prompt_part
            continue 
            
        # 2. New Part Detection
        if ("인트로" in line or "대본" in line) and ":" in line:
            parts = line.split(":", 1)
            possible_key = parts[0].strip()
            # Validate key format basically
            if any(k in possible_key for k in ["인트로", "대본"]):
                current_key = possible_key
                text_content = parts[1].strip()
                # Initialize
                data[current_key] = {'text': text_content, 'prompt': "", 'image': None}
                continue
        
        # 3. Append Text/Prompt to Current Part
        if current_key:
            # If we already have a prompt started, assume following lines are part of prompt 
            # UNLESS it looks like Korean text (this is heuristic, but prompts are English)
            # Actually, simpler: if prompt is empty, it's text. If prompt is filled, it might be continuation?
            # Safer: Just append to text UNLESS we explicitly saw a prompt marker. 
            # But wait, what if prompt is multi-line? 
            # Let's stick to appending to text unless we saw prompt marker on previous line? 
            # No, user screenshot shows prompt on same line. 
            # Let's assume prompt is usually single line or we treat extra lines as text for safety.
            
            # Refined strategy: If we haven't found a prompt for this section yet, it's text.
            if not data[current_key]['prompt']:
                 data[current_key]['text'] += " " + line
            else:
                 # If we already have a prompt, does this line look like a new section? (Handled by #2)
                 # Does it look like more English prompt? 
                 # Let's append to prompt if it's English-like, otherwise text?
                 # Too risk. Let's append to text if it's clearly Korean?
                 # For simplicity, let's assume prompt is one line for now (since we force inline).
                 # If user feedback says prompt is cut off, we fix later.
                 # BUT, if the line does NOT have prompt marker, we treat it as text (continuation of script).
                 # This might put prompt continuation into text, but better than losing script.
                 pass
                 # Revert: If we found prompt match above, we handled it.
                 # If we are here, no prompt match. So it is just text content.
                 # Only caveat: what if the script continues AFTER the prompt line? 
                 # (e.g. Text... [Prompt]... More Text). 
                 # The regex split handles Text... [Prompt].
                 # If next line is text, we append to text.
                 data[current_key]['text'] += " " + line
            
    return data

if st.session_state.step == 100:
    st.subheader("🔥 AI 공장 가동 중...")
    progress_bar = st.progress(0)
    status = st.empty()
    
    images_input = st.session_state.uploaded_images
    
    # 1. Titles
    status.text("1. 제목 생성 중...")
    if not st.session_state.titles:
        st.session_state.titles = sg.generate_titles(topic, target)
        # Simple selection logic
        try:
            ts = [t.strip() for t in st.session_state.titles.split('\n') if t.strip()]
            valid = [t for t in ts if t[0].isdigit() or t.startswith('-')]
            st.session_state.selected_title = valid[0].lstrip('0123456789. -* ') if valid else ts[0]
        except:
            st.session_state.selected_title = st.session_state.titles.split('\n')[0]
    progress_bar.progress(25)
    
    # 2. Outline
    status.text("2. 아웃라인 설계 중...")
    if not st.session_state.outline:
        st.session_state.outline = sg.generate_outline(st.session_state.selected_title, target, intro_count, body_count, combined_source, images_input)
    progress_bar.progress(50)
    
    # 3. Script & Prompts
    status.text("3. 대본 및 이미지 프롬프트 작성 중...")
    if not st.session_state.script_text_raw:
        st.session_state.script_text_raw = sg.generate_script(st.session_state.selected_title, st.session_state.outline, intro_count, body_count, combined_source, images_input)
        st.session_state.script_data = parse_script_with_prompts(st.session_state.script_text_raw)
    progress_bar.progress(75)

    # 4. Generate Images
    status.text("4. 이미지 생성 중 (일관성 유지)...")
    total_imgs = len(st.session_state.script_data)
    current_img_idx = 0
    
    # Create a place to display updates
    img_status = st.empty()
    
    for key, val in st.session_state.script_data.items():
        if val['prompt'] and val['image'] is None:
            img_status.text(f"이미지 생성 중... {key}")
            # Generate Image
            try:
                gen_img = sg.generate_image_from_prompt(val['prompt'])
                if gen_img:
                    st.session_state.script_data[key]['image'] = gen_img
            except Exception as e:
                print(f"Failed to generate for {key}")
        current_img_idx += 1
        progress_bar.progress(75 + int(25 * current_img_idx / total_imgs))
        
    st.balloons()
    status.text("완료!")
    st.session_state.step = 4

if st.session_state.step == 4:
    st.success(f"준비 완료: {st.session_state.selected_title}")
    
    with st.expander("아웃라인 보기"):
        st.write(st.session_state.outline)
        
    for key, val in st.session_state.script_data.items():
        with st.container():
            st.markdown(f'<div class="part-box">', unsafe_allow_html=True)
            st.markdown(f"### {key}")
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(val['text'])
                st.caption(f"🎨 Prompt: {val['prompt']}")
            with c2:
                if val['image']:
                    st.image(val['image'], use_column_width=True)
                else:
                    if val['prompt']:
                        if st.button(f"이미지 생성 ({key})", key=f"btn_{key}"):
                            new_img = sg.generate_image_from_prompt(val['prompt'], aspect_ratio=aspect_ratio_val)
                            if new_img:
                                st.session_state.script_data[key]['image'] = new_img
                                st.rerun()
                        st.warning("이미지 없음 (클릭하여 생성 시도)")
                    else:
                        st.info("프롬프트 없음")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Download logic (Text only)
    full_text = st.session_state.script_text_raw
    st.download_button("전체 대본 다운로드 (.txt)", full_text, file_name="script.txt")
    
    if st.button("처음으로"):
        st.session_state.step = 1
        st.rerun()
