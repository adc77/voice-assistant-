import streamlit as st
import pyaudio
import wave
import os
from original_pipeline import transcribe_audio, generate_response, text_to_speech

# Parameters for recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

def record_audio(filename):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    st.write("Recording... Click 'Stop Recording' when done.")
    
    while st.session_state.recording:
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    st.write(f"Audio saved as {filename}")
    return filename

# Streamlit UI
st.title("Speech-to-Speech Voice Assistant")

if 'recording' not in st.session_state:
    st.session_state.recording = False

if st.button("Start Recording"):
    if not st.session_state.recording:
        st.session_state.recording = True
        files = os.listdir("recordings")
        index = max([int(f[5:-4]) for f in files if f.startswith("audio") and f.endswith(".wav")], default=0) + 1
        output_filename = os.path.join("recordings", f"audio{index}.wav")
        record_audio(output_filename)

if st.button("Stop Recording"):
    if st.session_state.recording:
        st.session_state.recording = False

        # Now process the audio
        transcription_file = transcribe_audio(output_filename)
        response_file = generate_response(transcription_file)
        audio_output_file = text_to_speech(response_file)
        st.write("Playing the response...")
        st.audio(audio_output_file)
