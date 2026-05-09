def translate_and_speak(text, target_code):
    if not text or not text.strip():
        st.warning("No text detected to translate.")
        return
    
    try:
        # 1. SPLIT TEXT INTO CHUNKS (Max 3000 chars per chunk to be safe)
        max_chars = 3000
        chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
        
        full_translation = ""
        combined_audio = BytesIO()

        with st.spinner(f"Processing {len(chunks)} sections of text..."):
            for chunk in chunks:
                # Translate chunk
                translated_chunk = GoogleTranslator(source='auto', target=target_code).translate(chunk)
                full_translation += translated_chunk + " "
                
                # Generate Audio for chunk
                tts = gTTS(text=translated_chunk, lang=target_code)
                tts.write_to_fp(combined_audio)

        # Display full result
        st.info(f"**Translated Text:**\n\n{full_translation}")
        
        # Play combined audio
        combined_audio.seek(0)
        st.audio(combined_audio)

    except Exception as e:
        st.error(f"Error: {e}. Try selecting a smaller portion of the text.")
