import streamlit as st
from audio_recorder_streamlit import audio_recorder
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from PIL import Image
import pytesseract
import cv2
import numpy as np
from io import BytesIO

# --- CONFIG & HELPERS ---
st.set_page_config(page_title="PragyanAI Studio", layout="wide")
langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)

# Update this path if you are on Windows!
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def translate_and_speak(text, target_code):
    if not text.strip():
        st.warning("No text detected to translate.")
        return
    translated = GoogleTranslator(source='auto', target=target_code).translate(text)
    st.info(f"**Translated:** {translated}")
    tts = gTTS(text=translated, lang=target_code)
    tts_fp = BytesIO()
    tts.write_to_fp(tts_fp)
    st.audio(tts_fp)

# --- MAIN APP ---
def main():
    st.title("🌐 PragyanAI Multi-Model Studio")
    
    target_lang = st.sidebar.selectbox("Select Target Language", list(langs_dict.keys()))
    target_code = langs_dict[target_lang]

    tab1, tab2, tab3, tab4 = st.tabs(["🎥 Live Vision", "📸 Upload Image", "🎤 Voice", "📝 Text"])

    # --- TAB 1: LIVE VISION (Webcam) ---
    with tab1:
        st.subheader("Live Camera Translator")
        img_file_buffer = st.camera_input("Take a photo of text to translate")
        
        if img_file_buffer is not None:
            # To read image file buffer with OpenCV:
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            if st.button("Extract from Camera"):
                extracted_text = pytesseract.image_to_string(cv2_img)
                st.success(f"**Detected:** {extracted_text}")
                translate_and_speak(extracted_text, target_code)

    # --- TAB 2: IMAGE UPLOAD ---
    with tab2:
        img_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
        if img_file:
            img = Image.open(img_file)
            st.image(img, width=300)
            if st.button("Process Uploaded Image"):
                extracted_text = pytesseract.image_to_string(img)
                st.success(f"**Detected:** {extracted_text}")
                translate_and_speak(extracted_text, target_code)

    # --- TAB 3: VOICE ---
    with tab3:
        audio_bytes = audio_recorder(text="Click to record")
        if audio_bytes:
            st.audio(audio_bytes)
            if st.button("Process Voice"):
                recognizer = sr.Recognizer()
                with sr.AudioFile(BytesIO(audio_bytes)) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data)
                    st.success(f"**Transcription:** {text}")
                    translate_and_speak(text, target_code)

    # --- TAB 4: MANUAL TEXT ---
    with tab4:
        user_text = st.text_area("Type here...")
        if st.button("Translate Text"):
            translate_and_speak(user_text, target_code)

if __name__ == "__main__":
    main()
