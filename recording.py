import pyaudio
import wave
import os
import signal
import sys
from datetime import datetime

# Parameters for recording
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1  # Mono channel
RATE = 44100  # Sampling rate (44.1 kHz)
CHUNK = 1024  # Number of frames per buffer
RECORD_DIRECTORY = "recordings"

def signal_handler(sig, frame):
    print("\nRecording interrupted. Saving the audio...")
    global interrupted
    interrupted = True

def record_audio(filename):
    p = pyaudio.PyAudio()

    # Open the stream for recording
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    print("Recording... Press Ctrl+C to stop.")

    try:
        while not interrupted:
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nRecording stopped.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recording
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Audio saved as {filename}")

if __name__ == "__main__":
    if not os.path.exists(RECORD_DIRECTORY):
        os.makedirs(RECORD_DIRECTORY)

    signal.signal(signal.SIGINT, signal_handler)
    interrupted = False

    # Determine the filename
    files = os.listdir(RECORD_DIRECTORY)
    index = max([int(f[5:-4]) for f in files if f.startswith("audio") and f.endswith(".mp3")], default=0) + 1
    output_filename = os.path.join(RECORD_DIRECTORY, f"audio{index}.mp3")

    record_audio(output_filename)
