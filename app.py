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
import fitz  # PyMuPDF
from docx import Document # for .docx support

# --- CONFIG ---
st.set_page_config(page_title="PragyanAI Studio v2", layout="wide")

# --- CORE TRANSLATION ENGINE (With Chunking for long text) ---
def smart_translate_and_speak(text, target_code):
    if not text or not text.strip():
        st.warning("No text found to process.")
        return
    
    try:
        # Split text into 3000-character chunks to avoid API limits
        max_chars = 3000
        text_chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
        
        full_translation = ""
        combined_audio = BytesIO()

        with st.spinner(f"Translating {len(text_chunks)} sections..."):
            for chunk in text_chunks:
                # Translate
                translated_part = GoogleTranslator(source='auto', target=target_code).translate(chunk)
                full_translation += translated_part + " "
                
                # Audio
                tts = gTTS(text=translated_part, lang=target_code)
                tts.write_to_fp(combined_audio)

        st.success("✅ Translation Complete")
        st.info(full_translation)
        
        combined_audio.seek(0)
        st.audio(combined_audio)
        
    except Exception as e:
        st.error(f"Processing Error: {e}")

# --- DOCUMENT PARSERS ---
def get_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

def get_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# --- UI LAYOUT ---
def main():
    st.title("🌐 PragyanAI Multi-Model Studio")
    st.subheader("VVIET Workshop Edition")

    # Sidebar
    langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
    target_lang = st.sidebar.selectbox("Choose Target Language", list(langs_dict.keys()))
    target_code = langs_dict[target_lang]

    # Tabs
    tab_vision, tab_docs, tab_audio, tab_text = st.tabs([
        "📷 Visual OCR", "📄 Documents (PDF/DOCX)", "🎙️ Audio Lab", "✍️ Quick Text"
    ])

    # 1. VISUAL OCR (Live Camera)
    with tab_vision:
        cam_shot = st.camera_input("Scan physical document/text")
        if cam_shot:
            bytes_data = cam_shot.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            if st.button("Extract & Translate Camera"):
                text = pytesseract.image_to_string(img)
                smart_translate_and_speak(text, target_code)

    # 2. DOCUMENT HUB
    with tab_docs:
        uploaded_file = st.file_uploader("Upload Image, PDF, or DOCX", type=['png', 'jpg', 'pdf', 'docx'])
        if uploaded_file:
            ext = uploaded_file.name.split('.')[-1].lower()
            if st.button(f"Process {ext.upper()} File"):
                if ext == 'pdf':
                    extracted = get_text_from_pdf(uploaded_file)
                elif ext == 'docx':
                    extracted = get_text_from_docx(uploaded_file)
                else:
                    img = Image.open(uploaded_file)
                    extracted = pytesseract.image_to_string(img)
                
                st.text_area("Detected Text", extracted, height=150)
                smart_translate_and_speak(extracted, target_code)

    # 3. AUDIO LAB
    with tab_audio:
        mode = st.radio("Input Type", ["Microphone", "Upload File (WAV/FLAC)"])
        audio_src = audio_recorder() if mode == "Microphone" else st.file_uploader("Upload Audio", type=['wav', 'flac'])
        
        if audio_src:
            audio_bytes = audio_src if isinstance(audio_src, bytes) else audio_src.read()
            st.audio(audio_bytes)
            if st.button("Transcribe & Translate"):
                recognizer = sr.Recognizer()
                with sr.AudioFile(BytesIO(audio_bytes)) as source:
                    data = recognizer.record(source)
                    text = recognizer.recognize_google(data)
                    smart_translate_and_speak(text, target_code)

    # 4. QUICK TEXT
    with tab_text:
        raw_input = st.text_area("Paste text here...")
        if st.button("Run Text Translation"):
            smart_translate_and_speak(raw_input, target_code)

if __name__ == "__main__":
    main()
