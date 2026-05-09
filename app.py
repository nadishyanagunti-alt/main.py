import streamlit as st
from audio_recorder_streamlit import audio_recorder
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from PIL import Image
import pytesseract 
from io import BytesIO

# Setup Page
st.set_page_config(page_title="Multi-Model Translator", layout="wide")
langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)

def translate_and_speak(text, target_code):
    """Helper to handle translation and TTS"""
    translated = GoogleTranslator(source='auto', target=target_code).translate(text)
    st.info(f"**Translated:** {translated}")
    tts = gTTS(text=translated, lang=target_code)
    tts_fp = BytesIO()
    tts.write_to_fp(tts_fp)
    st.audio(tts_fp)

def main():
    st.title("🌐 PragyanAI Multi-Model Studio")
    target_lang = st.sidebar.selectbox("Target Language", list(langs_dict.keys()))
    target_code = langs_dict[target_lang]

    tab1, tab2, tab3 = st.tabs(["📸 Vision", "🎤 Voice", "📝 Text"])

    # --- TAB 1: VISION (Image to Text) ---
    with tab1:
        img_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
        if img_file:
            img = Image.open(img_file)
            st.image(img, width=300)
            if st.button("Extract & Translate Image"):
                # Simple OCR extraction
                extracted_text = pytesseract.image_to_string(img)
                st.success(f"**Detected Text:** {extracted_text}")
                translate_and_speak(extracted_text, target_code)

    # --- TAB 2: VOICE (Audio to Text) ---
    with tab2:
        audio_bytes = audio_recorder(text="Click to record voice")
        if audio_bytes:
            st.audio(audio_bytes)
            if st.button("Convert Voice"):
                recognizer = sr.Recognizer()
                with sr.AudioFile(BytesIO(audio_bytes)) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data)
                    st.success(f"**Transcription:** {text}")
                    translate_and_speak(text, target_code)

    # --- TAB 3: TEXT ---
    with tab3:
        user_text = st.text_area("Enter text to translate")
        if st.button("Translate Text"):
            if user_text:
                translate_and_speak(user_text, target_code)

if __name__ == "__main__":
    main()
