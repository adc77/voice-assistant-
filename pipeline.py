import os
import numpy as np
import pyaudio
import wave
import threading
from groq import Groq
import soundfile as sf
import torch
import playsound
from gtts import gTTS

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

def transcribe_audio(audio_file):
    print("Transcribing audio...")

    # Save the audio data to a temporary file
    temp_file = "temp_audio.wav"
    sf.write(temp_file, np.frombuffer(audio_data, dtype=np.int16), 48000)

    api_key = os.getenv('GROQ_API_KEY')
    #api_key = "GROQ_API_KEY"
    
     # Initialize the Groq client
    client = Groq(api_key=api_key)

    # Open the audio file
    with open(audio_file, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=(audio_file, file.read()),  # Required audio file
            model="distil-whisper-large-v3-en",  # Required model to use for transcription
            prompt="",  # Optional context or spelling prompt
            response_format="text",  # Set response format to 'text' for plain text output
            language="en",  # Optional language
            temperature=0.0  # Optional temperature for transcription creativity
        )
    
    os.remove(temp_file)
    return transcription

def generate_response(transcription_file):
    print("Generating response...")
    api_key = os.getenv('GROQ_API_KEY')
    
    client = Groq(api_key=api_key)

    with open(transcription_file, 'r') as file:
        user_message = file.read()

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "you are a concise and focused assistant that answers to the point without yapping."},
            {"role": "user", "content": user_message}
        ],
        model="llama3-8b-8192",
        temperature=0.2,
        max_tokens=50,
        top_p=0.9,
        stop=["\n"],
        stream=False,
    )

    response_content = chat_completion.choices[0].message.content
    return response_content

def text_to_speech(response_file):
    print("Converting text to speech...")
    
    tts = gTTS(text=input_text, lang='en')
    temp_file = "temp_output.mp3"
    tts.save(temp_file)
    
    # Read the audio file and return the binary data
    with open(temp_file, 'rb') as file:
        audio_data = file.read()
    
    os.remove(temp_file)
    return audio_data

