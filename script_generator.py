import google.generativeai as genai
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import io

def get_api_key():
    """Retrieves the Gemini API key from mcp_config.json."""
    config_path = Path("C:/Users/acepa/.gemini/antigravity/mcp_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["mcpServers"]["gemini"]["env"]["GEMINI_API_KEY"]
    except Exception as e:
        print(f"Error reading API key: {e}")
        return None

def configure_genai():
    api_key = get_api_key()
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def generate_titles(topic, target):
    if not configure_genai():
        return ["API Key Error"]
    
    model = genai.GenerativeModel('gemini-3-pro-preview')
    prompt = f"""
    You are a high-end AI script writer (Gemini 3 Pro).
    Topic: {topic}
    Target Audience: {target}
    
    Generate 5 catchy, click-worthy YouTube video titles in Korean.
    They should be engaging, curiosity-driven, and optimized for high CTR.
    Return ONLY the titles as a numbered list (1. Title). Do not include any other text.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_outline(title, target, intro_count, body_count, source_material="", images=None):
    if not configure_genai():
        return "API Key Error"
    
    model = genai.GenerativeModel('gemini-3-pro-preview')
    source_context = f"\n[Source Material/Reference]:\n{source_material}" if source_material else ""
    image_context = "\n[Visual Reference]: Images provided. Analyze them for details." if images else ""
    
    prompt_text = f"""
    You are a master storyteller for YouTube.
    Title: {title}
    Target Audience: {target}
    {source_context}
    {image_context}
    
    Task: Create a detailed narrative arc for a storytelling-style video.
    IMPORTANT: 
    1. If [Source Material] (text) is provided, prioritize specific facts from it.
    2. If [Visual Reference] (images) are provided, analyze them to extract visual details, atmosphere, or data and weave them into the narrative.
    
    The story should be divided into:
    1. **Intro Section**: {intro_count} distinct parts (Hook, Problem, Tease).
    2. **Body Section**: {body_count} logical story segments (Development, Climax, Resolution).
    
    Return the outline in Korean. 
    - Label Intro parts as: "인트로 1", "인트로 2", ...
    - Label Body parts as: "대본 1", "대본 2", ...
    """
    
    content = [prompt_text]
    if images:
        content.extend(images)
        
    response = model.generate_content(content)
    return response.text

def generate_script(title, outline, intro_count, body_count, source_material="", images=None, image_style="Cinematic", content_style="정보 전달/리뷰", video_length="10분"):
    if not configure_genai():
        return "API Key Error"
    
    model = genai.GenerativeModel('gemini-3-pro-preview')
    source_context = f"\n[Source Material/Reference]:\n{source_material}" if source_material else ""
    image_context = "\n[Visual Reference]: Images provided. Analyze them for details." if images else ""
    
    style_instruction = f"All image prompts MUST be strictly in '{image_style}' style." if image_style and image_style != "None" else "Maintain a consistent visual style throughout."

    # Content Style Prompt Logic - Updated for Bilingual Enforcement
    role_definition = f"You are a Bilingual AI Content Creator. Target Video Length: **{video_length}** (Extremely Important)."
    format_rule = "Content ONLY: No speaker labels unless specified below."
    
    if "인터뷰" in content_style or "대화형" in content_style:
        role_definition = f"You are a professional Interview Show Host. Target Length: **{video_length}**."
        format_rule = """
        **Script Format (INTERVIEW MODE)**:
        - Write the script as a **1:1 Conversation** between a HOST and a GUEST.
        - Use labels **'진행자(Host):'** and **'게스트(Guest):'** clearly.
        - The Host asks insightful questions based on the [Source Material].
        - The Guest answers naturally, explaining the facts or story.
        - Keep the tone conversational, engaging, and lively (Tiki-Taka).
        """
    elif "다큐멘터리" in content_style:
        role_definition = f"You are a documentary narrator. Target Length: **{video_length}**."
        format_rule = "Tone: Serious, emotional, and immersive narration."
    elif "동기부여" in content_style:
        format_rule = "Tone: Powerful, inspiring, and energetic."

    # Parse Video Length (e.g., "3분" -> 3)
    try:
        length_min = int(str(video_length).replace("분", "").strip())
    except:
        length_min = 10 # Default
        
    # Dynamic Instructions based on Length
    total_parts = intro_count + body_count
    
    if length_min <= 5:
        # SHORT FORM: Strict limiting
        target_total_words = length_min * 130 # Reduced from 160
        words_per_part = int(target_total_words / total_parts)
        
        length_instruction = f"""
        - **SHORT FORM / FAST PACED**: The video is ONLY {length_min} minutes.
        - **HARD LIMIT**: You must NOT exceed {target_total_words} words in total.
        - **Per Section Limit**: Each 'Intro' or 'Body' part must be approx **{words_per_part} words**.
        - Keep it CONCISE. Cut out all fluff. Get straight to the point.
        - If you write too much, the video will be too long. STOP when you made the point.
        """
    elif length_min <= 10:
        # STANDARD
        target_total_words = length_min * 150
        length_instruction = f"""
        - **STANDARD YOUTUBE LENGTH**: The video is {length_min} minutes.
        - Total Target: ~{target_total_words} words.
        - Provide good detail but maintain good pacing.
        """
    else:
        # LONG FORM
        target_total_words = length_min * 180
        length_instruction = f"""
        - **LONG FORM / DEEP DIVE**: The video is {length_min} minutes.
        - You MUST write a **VERY LONG, HIGHLY DETAILED** script.
        - Expand every point. Elaborate on every detail. Provide deep analysis.
        - Total Target: ~{target_total_words} words.
        """

    prompt_text = f"""
    {role_definition}
    Title: {title}
    Outline:
    {outline}
    {source_context}
    
    Task: Write a FULL script following these strict rules:
    
    **[CRITICAL LENGTH RULE]**:
    - The **TOTAL VIDEO LENGTH** is **{video_length}**.
    {length_instruction}
    - **DO NOT Summarize.** Write the full spoken word content.
    
    **[CRITICAL LANGUAGE RULES]**:
    - **Script Content**: MUST be in **Korean** only.
    - **NO IMAGE PROMPTS**: Do NOT generate any image prompts in this step. Just write the script text.
    
    1. **Script Format**: 
       - Generate {intro_count} Intro parts labeled "인트로 1: ", "인트로 2: ", ...
       - Generate {body_count} Body parts labeled "대본 1: ", "대본 2: ", ...
       - **Style & Tone**: {content_style}
       - {format_rule}
       
    2. **Fact-Based & Visual Storytelling**: 
       - Use specific data/stories from [Source Material].
       
    Example Output:
    인트로 1: 
    진행자: (한국어 대본 내용...)
    
    대본 1:
    게스트: (한국어 대본 내용...)
    """
    
    content = [prompt_text]
    # Images are not needed for script writing strictly, but context helps. Keep if available.
    if images:
        content.extend(images)

    response = model.generate_content(content)
    return response.text
# Duplicate code section removed
def create_image_prompt(script_text, style_instruction):
    print(f"[DEBUG] Generating prompt for style: {style_instruction}")
    if not configure_genai():
        # FALLBACK 1: No Auth
        style_clean = style_instruction.replace("Target Style:", "").strip()
        return f"Hyper-realistic {style_clean}, 2k resolution, cinematic lighting, masterpiece, detailed texture, unreal engine 5 render" 
    
    try:
        # Model Fallback List
        models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        result = None
        last_error = None

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"""
                You are an AI Visual Director.
                Task: Create a detailed **ENGLISH** image generation prompt.
                
                Input: "{script_text}"
                Style: {style_instruction}
                
                Rules:
                1. English ONLY. No Korean text.
                2. **Context: Modern South Korea.** usage Korean characters, Korean streets/architecture, and Korean atmosphere.
                3. Detailed visual description including lighting, texture.
                4. Include: "2k resolution", "highly detailed".
                5. 30-50 words.
                """
                response = model.generate_content(prompt)
                result = response.text.strip()
                if result:
                    break
            except Exception as e:
                last_error = e
                print(f"Model {model_name} failed: {e}")
                continue
        
        if not result:
            print(f"All models failed. Last error: {last_error}")
            style_clean = style_instruction.replace("Target Style:", "").strip()
            return f"Masterpiece, best quality, {style_clean}, 2k resolution, cinematic lighting, highly detailed (Fallback: {str(last_error)})"

        # Safety Check: STRICT ENGLISH ONLY
        # If Korean is detected, try to TRANSLATE it instead of failing.
        if re.search("[가-힣]", result):
            print(f"[DEBUG] Korean detected in prompt: {result}. Attempting translation...")
            try:
                trans_model = genai.GenerativeModel('gemini-1.5-flash')
                trans_prompt = f"Translate this image prompt to English ONLY. Do not add explanations. Text: {result}"
                trans_response = trans_model.generate_content(trans_prompt)
                result = trans_response.text.strip()
                # Double check
                if re.search("[가-힣]", result):
                    # Still Korean? fallback but keep style
                    style_clean = style_instruction.replace("Target Style:", "").strip()
                    return f"High quality, {style_clean}, dramatic angle, 2k resolution, highly detailed"
            except:
                 # Translation failed
                 pass

        if not result:
             style_clean = style_instruction.replace("Target Style:", "").strip()
             return f"Best quality, {style_clean}, dramatic angle, 2k resolution, highly detailed, cinematic lighting"
            
        return result \
               + ", 2k resolution" if "2k resolution" not in result else result
    except Exception as e:
        print(f"[ERROR] Prompt gen failed: {e}")
        # FALLBACK 2: API Error
        style_clean = style_instruction.replace("Target Style:", "").strip()
        return f"Masterpiece, best quality, {style_clean}, 2k resolution, cinematic lighting, highly detailed"


def crop_to_aspect_ratio(image, aspect_ratio="9:16"):
    """
    Crops an image (PIL.Image) to the specified aspect ratio.
    Default is 9:16 (Shorts).
    """
    if aspect_ratio == "9:16":
        target_ratio = 9 / 16
    elif aspect_ratio == "16:9":
        target_ratio = 16 / 9
    else:
        return image # Return original if ratio not supported/needed

    img_width, img_height = image.size
    current_ratio = img_width / img_height
    
    # Allow small tolerance
    if abs(current_ratio - target_ratio) < 0.01:
        return image

    # Calculate new dimensions
    if current_ratio > target_ratio:
        # Image is too wide, crop width
        new_width = int(img_height * target_ratio)
        new_height = img_height
        left = (img_width - new_width) / 2
        top = 0
        right = new_width + left
        bottom = img_height
    else:
        # Image is too tall, crop height
        new_width = img_width
        new_height = int(img_width / target_ratio)
        top = (img_height - new_height) / 2
        left = 0
        bottom = new_height + top
        right = img_width
        
    return image.crop((left, top, right, bottom))

def generate_image_from_prompt(prompt, aspect_ratio="16:9"):
    """Generates an image using Gemini with fallback and cropping."""
    if not configure_genai():
        print("Auth failed")
        return None
    
    # Clean prompt
    clean_prompt = prompt.replace("*", "").replace("Image Prompt:", "").strip()
    generated_image = None
    
    # Determine target ratio string for prompt
    ratio_prompt = "vertical 9:16" if "9:16" in aspect_ratio else "cinematic 16:9"
    ar_val = "9:16" if "9:16" in aspect_ratio else "16:9"

    try:
        # PRIMARY: gemini-2.0-flash-exp-image-generation
        prompt_with_ar_primary = f"Generate a {ratio_prompt} image of {clean_prompt}, aspect_ratio {ar_val}"
        print(f"Trying Primary Model (2.0-flash-exp) with prompt: {prompt_with_ar_primary[:50]}...")
        
        try:
             model_primary = genai.GenerativeModel("models/gemini-2.0-flash-exp-image-generation")
             response = model_primary.generate_content(prompt_with_ar_primary)
             
             if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        generated_image = Image.open(io.BytesIO(image_data))
                        print("Primary model passed.")
                        break
        except Exception as e:
            print(f"Primary Image Gen Failed (2.0-flash-exp): {e}")

        # FALLBACK: gemini-2.5-flash-image
        if not generated_image:
            print("Falling back to gemini-2.5-flash-image...")
            try:
                # This model needs a text prompt instruction, but might still be square
                prompt_fallback = f"Generate an image of {clean_prompt}, aspect ratio {aspect_ratio}" 
                
                model_fallback = genai.GenerativeModel("models/gemini-2.5-flash-image")
                response = model_fallback.generate_content(prompt_fallback)
                
                if response.parts:
                    for part in response.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_data = part.inline_data.data
                            generated_image = Image.open(io.BytesIO(image_data))
                            print("Fallback model passed.")
                            break
            except Exception as e2:
                 print(f"Fallback Image Gen Failed: {e2}")

        if generated_image:
            # FORCE CROP to ensuring aspect ratio compliance
            print(f"Original Image Size: {generated_image.size}")
            
            # Check if user requested 9:16 (Shorts)
            if "9:16" in aspect_ratio:
                 print("Applying 9:16 Crop...")
                 final_image = crop_to_aspect_ratio(generated_image, "9:16")
                 print(f"Final Image Size: {final_image.size}")
                 return final_image
            elif "16:9" in aspect_ratio or "유튜브" in aspect_ratio:
                 print("Applying 16:9 Crop...")
                 final_image = crop_to_aspect_ratio(generated_image, "16:9")
                 print(f"Final Image Size: {final_image.size}")
                 return final_image
            
            return generated_image

        print("No image generated from any model.")
        return None
    except Exception as e:
        print(f"Image gen critical failure: {e}")
        return None 

def translate_to_english(text):
    """Translates text to English for image prompting using Gemini."""
    if not configure_genai():
        return text 
    
    try:
        # Use gemini-1.5-flash for translation
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Translate to English image prompt: "{text}"
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text
