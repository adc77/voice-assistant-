import streamlit as st
import pyaudio
import wave
import threading
import os
from original_pipeline import transcribe_audio, generate_response, text_to_speech

# Global variables
interrupted = False
output_filename = None

# Parameters for recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

def stop_recording():
    global interrupted
    interrupted = True

def record_audio():
    global interrupted
    global output_filename

    st.write("Recording... (Click 'Stop' to end recording)")
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    interrupted = False
    while not interrupted:
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    if not os.path.exists("recordings"):
        os.makedirs("recordings")

    # Naming the audio file
    files = os.listdir("recordings")
    index = max([int(f[5:-4]) for f in files if f.startswith("audio") and f.endswith(".wav")], default=0) + 1
    output_filename = os.path.join("recordings", f"audio{index}.wav")

    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    st.write(f"Audio saved as {output_filename}")
    return output_filename

# Streamlit UI
st.title("Speech-to-Speech Voice Assistant")
st.write("Click 'Start' to begin recording and 'Stop' to finish. The processed response will be played back automatically.")

start_button = st.button("Start Recording")
stop_button = st.button("Stop Recording")

if start_button:
    if 'recording_thread' in st.session_state and st.session_state.recording_thread.is_alive():
        st.write("Recording already in progress...")
    else:
        st.session_state.recording_thread = threading.Thread(target=record_audio)
        st.session_state.recording_thread.start()

if stop_button:
    stop_recording()
    if 'recording_thread' in st.session_state and st.session_state.recording_thread.is_alive():
        st.session_state.recording_thread.join()  # Wait for recording to finish
        st.write("Recording stopped.")
        if output_filename:
            transcription_file = transcribe_audio(output_filename)
            response_file = generate_response(transcription_file)
            audio_output_file = text_to_speech(response_file)
            st.write("Playing the response...")
            st.audio(audio_output_file)
