import streamlit as st
import script_generator as sg
import json
import os
import re
from PIL import Image
import io
import zipfile
import google.generativeai as genai

st.set_page_config(page_title="유튜브 대본 공장 (Anti-Korean)", page_icon="🍌", layout="wide")

# Internal Function to bypass module caching issues & Block Korean

def load_mcp_api_key():
    """Loads Gemini API Key from MCP config file."""
    try:
        config_path = r"C:\Users\acepa\.gemini\antigravity\mcp_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                gemini_env = config.get("mcpServers", {}).get("gemini", {}).get("env", {})
                api_key = gemini_env.get("GEMINI_API_KEY")
                if api_key:
                    # Set ENV for other modules
                    os.environ["GEMINI_API_KEY"] = api_key
                    return api_key
    except Exception as e:
        print(f"Failed to load MCP config: {e}")
    
    # Fallback to Streamlit Secrets (for Netlify/Streamlit Cloud)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            os.environ["GEMINI_API_KEY"] = api_key
            return api_key
    except:
        pass
        
    return None

def translate_topic_to_english_simple(text):
    # Try to translate using the API if possible
    try:
        api_key = load_mcp_api_key()
        if not api_key: api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            resp = model.generate_content(f"Translate to English (just the noun/phrase, no explanation): {text}")
            return resp.text.strip()
    except:
        pass
        
    return "" 

def internal_create_prompt(text, style):
    """Generates prompt directly within app.py to avoid caching issues."""
    try:
        # 1. MCP Auto-Load
        api_key = load_mcp_api_key()
        
        # 2. Try environment variable (fallback)
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        
        # 3. Try session state (Manual Input)
        if not api_key and 'user_api_key' in st.session_state:
            api_key = st.session_state['user_api_key']
            
        if not api_key:
            return f"Error: No API Key. {style}, 2k resolution, detailed"

        genai.configure(api_key=api_key)
        
        # Model Fallback List
        models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        result = None
        last_error = None

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                
                prompt = f"""
                Act as an AI Visual Director.
                Task: Create a detailed **ENGLISH** image generation prompt based on the following script segment.
                
                Script Segment: "{text}"
                Style: {style}
                
                CMD:
                1. Analyze the script segment using a **South Korean context** (Backgrounds, Characters, Architecture, Atmosphere must be Korean).
                2. Write a highly detailed image prompt in **ENGLISH ONLY**.
                3. Describe visible elements:
                   - Characters: Korean facial features, modern Korean fashion.
                   - Background: Seoul streets, Korean apartments, Han River, or relevant Korean locations.
                   - Atmosphere: Matches the script but grounded in Korea.
                4. ABSOLUTELY NO KOREAN TEXT in the output.
                5. Length: 40-60 words.
                
                Output ONLY the English prompt.
                """
                response = model.generate_content(prompt)
                result = response.text.strip()
                if result:
                    break # Success
            except Exception as e:
                last_error = e
                print(f"Model {model_name} failed: {e}")
                continue
        
        if not result:
            print(f"All models failed. Last error: {last_error}")
            return f"High quality image, {style.replace('Target Style:', '')}, 2k resolution, detailed (Fallback: {str(last_error)})"
        
        # Override if Korean detected
        if re.search("[가-힣]", result):
            print(f"Korean usage detected in: {result}")
            # Attempt Translation
            try:
                trans_model = genai.GenerativeModel('gemini-1.5-flash')
                trans_prompt = f"Translate this image prompt to English ONLY. No explanations. Text: {result}"
                trans_response = trans_model.generate_content(trans_prompt)
                result = trans_response.text.strip()
            except:
                pass
                
            if re.search("[가-힣]", result):
                clean_style = style.replace("Target Style:", "").strip()
                # Try to extract a keyword from text if possible? Too risky.
                return f"High quality, {clean_style}, cinematic lighting, highly detailed, 2k resolution, masterpiece"
            
        return result
    except Exception as e:
        print(f"Inline Gen Error: {e}")
        return f"High quality image, {style.replace('Target Style:', '')}, 2k resolution, detailed"

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

st.title("🏭 유튜브 스토리텔링 대본 공장 (v4.3 FINAL Fresh Start)")
st.caption("Nano Banana Pro 엔진 탑재 | MCP 자동 연결 | **강력한 한글 차단**")
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
    st.header("🔑 API 키 설정 (필수)")
    
    # Check Env & MCP
    mcp_key = load_mcp_api_key()
    env_key = os.getenv("GEMINI_API_KEY")
    manual_key = st.session_state.get('user_api_key', '')
    
    if mcp_key:
        st.success(f"MCP 자동 연결됨 (via mcp_config.json)")
    elif env_key:
        st.success(f"시스템 키 사용 중 (연결됨)")
    elif manual_key:
        os.environ["GEMINI_API_KEY"] = manual_key
        st.success(f"수동 키 사용 중 (연결됨)")
    else:
        st.error("API 키가 없습니다!")
        user_key_input = st.text_input("여기에 API Key를 붙여넣으세요", type="password")
        if user_key_input:
            st.session_state['user_api_key'] = user_key_input
            os.environ["GEMINI_API_KEY"] = user_key_input
            st.rerun()
            
    st.markdown("---")
    
    # Safe Reset Logic using Callback
    def reset_app_state():
        saved_key = st.session_state.get('user_api_key', '')
        st.session_state.clear()
        if saved_key:
            st.session_state['user_api_key'] = saved_key
        st.session_state['reset_success'] = True

    if st.button("💥 모든 상태 초기화 (Super Hard Reset)", type="secondary", on_click=reset_app_state):
        pass

    if st.session_state.get('reset_success', False):
        st.success("✅ 데이터 완전 삭제 완료!")
        # Clear the flag so it doesn't persist
        del st.session_state['reset_success']

    import datetime
    dt_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.info(f"🕒 현재 시간: {dt_now} (v4.3 Running)")


    st.divider()
    
    st.header("⚙️ 콘텐츠 설정")
    # Force Mode
    use_template_only = st.checkbox("영문 템플릿 강제 사용 (AI 미사용)", value=True, help="체크하면 AI 생성을 건너뛰고 100% 안전한 영문 템플릿만 사용합니다.")
    topic = st.text_input("콘텐츠 주제", value="", placeholder="예: 2024년 유튜브 트렌드", key="input_topic_v3")
    target = st.text_input("시청 대상", value="", placeholder="예: 2030 직장인", key="input_target_v4")
    
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
    video_length = st.selectbox("총 영상 길이", options=length_options, index=idx_10min)
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

def parse_script_only(full_text):
    data = {}
    current_key = None
    lines = full_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # New Part Detection (Simple)
        if ("인트로" in line or "대본" in line) and ":" in line:
            parts = line.split(":", 1)
            possible_key = parts[0].strip()
            # Validate key format
            if any(k in possible_key for k in ["인트로", "대본"]):
                current_key = possible_key
                text_content = parts[1].strip()
                data[current_key] = {'text': text_content, 'prompt': "", 'image': None}
                continue
        
        # Append Text
        if current_key:
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
        try:
            ts = [t.strip() for t in st.session_state.titles.split('\n') if t.strip()]
            valid = [t for t in ts if t[0].isdigit() or t.startswith('-')]
            st.session_state.selected_title = valid[0].lstrip('0123456789. -* ') if valid else ts[0]
        except:
            st.session_state.selected_title = st.session_state.titles.split('\n')[0]
    progress_bar.progress(20)
    
    # 2. Outline
    status.text("2. 아웃라인 설계 중...")
    if not st.session_state.outline:
        st.session_state.outline = sg.generate_outline(st.session_state.selected_title, target, intro_count, body_count, combined_source, images_input)
    progress_bar.progress(40)
    
    # 3. Script (Text Only)
    status.text("3. 대본 작성 중 (순수 한국어)...")
    if not st.session_state.script_text_raw:
        st.session_state.script_text_raw = sg.generate_script(st.session_state.selected_title, st.session_state.outline, intro_count, body_count, combined_source, images_input, img_style_val, content_style, video_length)
        st.session_state.script_data = parse_script_only(st.session_state.script_text_raw)
    progress_bar.progress(60)

    # 4. Image Prompt Engineering (Separate Step)
    status.text("4. 프롬프트 생성 엔진 가동 (Engine: Nano Banana Pro)...")
    
    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        st.info("프롬프트가 보이지 않거나 생성이 멈추면 **오른쪽 버튼**을 눌러주세요. 👉")
    with col_p2:
        if st.button("🔄 프롬프트 강제 재생성", type="primary", key="btn_force_regen"):
            for k in st.session_state.script_data:
                st.session_state.script_data[k]['prompt'] = None
            st.rerun()

    total_parts = len(st.session_state.script_data)
    current_idx = 0
    
    with st.expander("🍌 Nano Banana Pro 프롬프트 생성 로그 (v3.3 Auto-Clean)", expanded=True):
        st.caption("실시간 감시 중: 한글이나 불량 데이터가 발견되면 즉시 소각하고 재생성합니다.")
        for key, val in st.session_state.script_data.items():
            # AUTO-PURGE: Check for bad data in existing prompts
            current_prompt = val.get('prompt', '')
            
            # Condition 1: Empty or too short
            is_bad_length = not current_prompt or len(current_prompt) < 10
            # Condition 2: Old fallback garbage
            is_old_garbage = "High quality image" in current_prompt and "detailed" not in current_prompt
            # Condition 3: KOREAN DETECTED (Critical)
            is_korean = bool(re.search("[가-힣]", current_prompt))
            
            if is_bad_length or is_old_garbage or is_korean:
                if is_korean:
                    st.toast(f"🚨 한글 오염 감지됨 ([{key}]). 자동 정화 시작...", icon="🔥")
                st.session_state.script_data[key]['prompt'] = None
                
            if not st.session_state.script_data[key]['prompt']:
                st.write(f"🚀 **[{key}]** 생성 시도 중...")
                # Call separate prompt generator
                # Map Korean styles to English
                style_map = {
                    "Anime": "Anime style, vibrant colors",
                    "Realistic Photo": "Photorealistic, 2k resolution",
                    "Cinematic": "Cinematic lighting, movie scene",
                    "Pixar Style": "3D render, Pixar style",
                    "Documentary": "Documentary style, realistic",
                    "Vlog": "Vlog style, natural lighting",
                    "Vintage": "Vintage film look, grainy",
                    "Film Look": "Movie quality, cinematic",
                    "Game Art": "Game art style, high quality",
                    "None": "High quality"
                }
                
                english_style = style_map.get(img_style_val, "Cinematic, High quality")
                style_str = f"Target Style: {english_style}"
                
                try:
                    # Use INTERNAL function to guarantee update & Anti-Korean
                    eng_prompt = internal_create_prompt(val['text'], style_str)
                    
                    # Double Check (Paranoia Mode)
                    if re.search("[ㄱ-ㅎ가-힣ㅏ-ㅣ]", eng_prompt) or not eng_prompt or "Error" in eng_prompt:
                        eng_prompt = f"High quality {english_style}, cinematic lighting, detailed, 2k resolution, masterpiece"
                        
                except Exception as e:
                    eng_prompt = f"High quality {english_style}, cinematic, 2k resolution"
                
                # Cleanup
                eng_prompt = str(eng_prompt).replace("**", "").replace("Image Prompt:", "").replace("Prompt:", "").strip()
                
                # Final Safety Net
                if re.search("[ㄱ-ㅎ가-힣ㅏ-ㅣ]", eng_prompt):
                     eng_prompt = f"High quality {english_style}, cinematic lighting, detailed, 2k resolution"


                # Check cleanliness
                if "Error" in eng_prompt:
                    st.error(f"**[{key}]** 실패: {eng_prompt}")
                    # Emergency Fallback
                    eng_prompt = f"{english_style}, masterpiece, 2k resolution, detailed, dramatic lighting"
                else:
                    st.success(f"**[{key}]** 성공: `{eng_prompt[:50]}...`")
                
                st.session_state.script_data[key]['prompt'] = eng_prompt
            else:
                st.info(f"**[{key}]** 프롬프트 완료: `{str(st.session_state.script_data[key]['prompt'])[:40]}...`")
                
            current_idx += 1
    progress_bar.progress(80)

    # 5. Generate Images (Nano Banana Pro)
    status.text("5. Nano Banana Pro가 이미지를 그리고 있습니다... (약 10~20초 소요)")
    img_status = st.empty()
    current_img_idx = 0
    
    for key, val in st.session_state.script_data.items():
        if val['prompt'] and val['image'] is None:
            img_status.text(f"🎨 그리는 중: {key} ...")
            try:
                gen_img = sg.generate_image_from_prompt(val['prompt'], aspect_ratio=aspect_ratio_val)
                if gen_img:
                    st.session_state.script_data[key]['image'] = gen_img
            except Exception as e:
                print(f"Failed to generate for {key}: {e}")
        current_img_idx += 1
        progress_bar.progress(80 + int(20 * (current_img_idx /  (total_parts if total_parts > 0 else 1))))
        
    st.balloons()
    status.text("완료!")
    st.success("Nano Banana Pro가 모든 작업을 완료했습니다!")
    status.text("완료!")
    st.session_state.step = 4

if st.session_state.step == 4:
    st.success(f"준비 완료: {st.session_state.selected_title}")
    
    # Emergency Clean Button
    with st.expander("🚨 데이터 긴급 수정 도구 (한글이 보이면 클릭하세요)", expanded=True):
        col_clean1, col_clean2 = st.columns([3, 1])
        with col_clean1:
            st.warning("프롬프트에 한글이 섞여있거나 이미지가 나오지 않나요?")
        with col_clean2:
            if st.button("🧹 전체 프롬프트 강제 정화", type="primary"):
                cleaned_count = 0
                for k, v in st.session_state.script_data.items():
                    p = str(v.get('prompt', ''))
                    # Broad Korean Check
                    if re.search("[ㄱ-ㅎ가-힣ㅏ-ㅣ]", p) or "파싱된" in p or not p:
                        clean_style = img_style_val if "img_style_val" in globals() else "Cinematic"
                        new_p = f"High quality {clean_style}, cinematic lighting, detailed, 2k resolution, masterpiece"
                        st.session_state.script_data[k]['prompt'] = new_p
                        cleaned_count += 1
                st.success(f"{cleaned_count}개의 오염된 프롬프트를 정화했습니다! 화면이 새로고침됩니다.")
                st.rerun()

    with st.expander("아웃라인 보기"):
        st.write(st.session_state.outline)
        
    with st.expander("원본 대본 확인 (Debug)"):
        st.text_area("Raw Script", st.session_state.script_text_raw, height=300)
        
    for key, val in st.session_state.script_data.items():
        with st.container():
            st.markdown(f'<div class="part-box">', unsafe_allow_html=True)
            st.markdown(f"### {key}")
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(val['text'])
                
                # --- AUTO-CORRECT LOGIC (Step 4) ---
                current_prompt = str(val.get('prompt', ''))
                
                # Check for Korean, Empty, or Garbage
                has_korean = bool(re.search("[ㄱ-ㅎ가-힣ㅏ-ㅣ]", current_prompt)) or "파싱된" in current_prompt
                is_garbage = "High quality image" in current_prompt and len(current_prompt) < 20
                is_empty = not current_prompt
                
                # Checkbox forced override
                force_template = False
                if 'use_template_only' in locals() or 'use_template_only' in globals():
                     if use_template_only: force_template = True

                if force_template or is_empty or has_korean or is_garbage:
                    # On-the-fly Correction
                    clean_style = img_style_val if "img_style_val" in locals() else "Cinematic"
                    if "Target Style:" in clean_style: clean_style = clean_style.replace("Target Style:", "")
                    
                    
                    
                    # Try to use TITLE or TOPIC for relevance in fallback
                    
                    # 1. Try to RE-GENERATE from Script Content (Best Quality)
                    re_generated_prompt = ""
                    try:
                        re_generated_prompt = internal_create_prompt(val['text'], clean_style)
                    except Exception as e:
                        print(f"Regen failed: {e}")

                    if re_generated_prompt and not re.search("[ㄱ-ㅎ가-힣ㅏ-ㅣ]", re_generated_prompt) and "Error:" not in re_generated_prompt:
                         new_prompt = f"[Content-Aware] {re_generated_prompt}"
                    else:
                        # 2. Fallback: Translation of old prompt (if it had content)
                        translated_p = ""
                        if has_korean and not is_empty:
                             try:
                                 translated_p = translate_topic_to_english_simple(current_prompt)
                             except:
                                 pass
                        
                        if translated_p and not re.search("[ㄱ-ㅎ가-힣ㅏ-ㅣ]", translated_p):
                            new_prompt = f"[Translated] {translated_p}, 2k resolution"
                        else:
                            # 3. Fallback: Topic
                            topic_context = st.session_state.get('input_topic_v3', '') or st.session_state.get('selected_title', '')
                            topic_slug =  translate_topic_to_english_simple(topic_context) if topic_context else ""
                            
                            if topic_slug:
                                 new_prompt = f"[Topic] High quality {clean_style}, {topic_slug}, cinematic lighting, detailed, 2k resolution, masterpiece"
                            else:
                                 new_prompt = f"[Default] High quality {clean_style}, cinematic lighting, detailed, 2k resolution, masterpiece"
                    
                    # Update Session & Current Variable
                    st.session_state.script_data[key]['prompt'] = new_prompt
                    current_prompt = new_prompt
                # -----------------------------------

                if current_prompt:
                    st.info(f"🎨 Image Prompt (Eng): {current_prompt}")
                else:
                    st.warning("⚠️ 프롬프트가 파싱되지 않았습니다.")
            with c2:
                if val['image']:
                    st.image(val['image'], use_container_width=True)
                    # Individual Download Button
                    try:
                        img_byte_arr = io.BytesIO()
                        val['image'].save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()
                        st.download_button(
                            label=f"📥 이미지 다운로드 ({key})",
                            data=img_byte_arr,
                            file_name=f"{key}_image.png",
                            mime="image/png",
                            key=f"dl_btn_{key}"
                        )
                    except Exception as e:
                        st.error(f"다운로드 버튼 생성 실패: {e}")
                else:
                    if val['prompt']:
                        if st.button(f"이미지 생성 ({key})", key=f"btn_{key}"):
                            try:
                                new_img = sg.generate_image_from_prompt(val['prompt'], aspect_ratio=aspect_ratio_val)
                                if new_img:
                                    st.session_state.script_data[key]['image'] = new_img
                                    st.rerun()
                                else:
                                    st.error("이미지 생성 실패 (모델 응답 없음)")
                            except Exception as e:
                                st.error(f"에러 발생: {e}")
                        st.warning("이미지 없음 (클릭하여 생성 시도)")
                    else:
                        st.error("프롬프트가 없어 생성 불가")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Download logic (Separated)
    final_script_txt = ""
    final_script_txt += f"Title: {st.session_state.selected_title}\n"
    final_script_txt += f"Topic: {topic}\n"
    final_script_txt += "=" * 40 + "\n\n"
    
    # Section 1: Memory/Script (Korean)
    final_script_txt += "=== [1] KOREAN SCRIPT ===\n\n"
    for key, val in st.session_state.script_data.items():
        final_script_txt += f"[{key}]\n"
        final_script_txt += f"{val['text']}\n\n"
        
    final_script_txt += "\n" + "=" * 40 + "\n\n"
    
    # Section 2: Image Prompts (English)
    final_script_txt += "=== [2] ENGLISH IMAGE PROMPTS ===\n\n"
    for key, val in st.session_state.script_data.items():
        if val.get('prompt'):
            final_script_txt += f"[{key} Image]\n"
            final_script_txt += f"{val['prompt']}\n\n"
            
    c_dl1, c_dl2 = st.columns(2)
    with c_dl1:
        st.download_button("📜 전체 대본 다운로드 (.txt)", final_script_txt, file_name="script_with_prompts.txt", use_container_width=True)
    
    # Local Save Logic
    with c_dl2:
        # Default path
        default_path = os.path.join(os.getcwd(), "saved_results")
        save_root = st.text_input("📂 저장할 폴더 경로 (변경 가능)", value=default_path)
        
        if st.button("💾 이 경로에 저장하기", type="primary", use_container_width=True):
            try:
                # Create Base Directory if not exists
                if not os.path.exists(save_root):
                    os.makedirs(save_root)
                
                # Create Timestamped Folder INSIDE the chosen root
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(save_root, timestamp)
                os.makedirs(save_path)
                
                # 1. Save Script
                with open(os.path.join(save_path, "script.txt"), "w", encoding="utf-8") as f:
                    f.write(final_script_txt)
                
                # 2. Save Images
                saved_count = 0
                for key, val in st.session_state.script_data.items():
                    if val.get('image'):
                        img_filename = f"{key}.png"
                        val['image'].save(os.path.join(save_path, img_filename))
                        saved_count += 1
                
                # Success Message
                if saved_count > 0:
                    st.success(f"✅ 저장 완료!\n\n`{os.path.abspath(save_path)}`")
                    st.balloons()
                    # Open folder in explorer (Windows only)
                    try:
                        os.startfile(os.path.abspath(save_path))
                    except:
                        pass
                else:
                    st.warning("저장할 이미지가 없습니다.")
                    
            except Exception as e:
                st.error(f"저장 실패: {e}")
    
    if st.button("처음으로", type="secondary", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
