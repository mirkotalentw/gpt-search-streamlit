from st_audiorec import st_audiorec
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from io import BufferedReader, BytesIO
import soundfile as sf

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
 
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not found.")
 
OpenAI.api_key = openai_api_key
 
client = OpenAI()

wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    
    audio_file = BytesIO(wav_audio_data)
    audio_file.name = "audio.wav" 

    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        response_format="text",
        language="en"
    )
    st.write(transcription)
