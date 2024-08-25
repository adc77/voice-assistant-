import os
import pyaudio
import wave
import threading
from faster_whisper import WhisperModel
from groq import Groq
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import soundfile as sf
import torch
import playsound

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# Parameters for recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_DIRECTORY = "recordings"
TRANSCRIPTION_DIR = "transcriptions"
RESPONSE_DIR = "responses"
OUTPUT_DIR = "output"

interrupted = False

def stop_recording():
    input("Press Enter to stop recording...\n")
    global interrupted
    interrupted = True

def record_audio(filename):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    print("Recording...")
    threading.Thread(target=stop_recording).start()

    while not interrupted:
        data = stream.read(CHUNK)
        frames.append(data)

    print("\nRecording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Audio saved as {filename}")

def transcribe_audio(audio_file):
    model_size = "large-v3"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_file, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500))

    transcription_index = max([int(f[len('transcription'):-4]) for f in os.listdir(TRANSCRIPTION_DIR) if f.startswith("transcription") and f.endswith(".txt")], default=0) + 1
    transcription_file = os.path.join(TRANSCRIPTION_DIR, f"transcription{transcription_index}.txt")

    with open(transcription_file, "w") as f:
        for segment in segments:
            f.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n")

    print(f"Transcription saved to {transcription_file}")
    return transcription_file

def generate_response(transcription_file):
    #api_key = os.getenv('GROQ_API_KEY')
    api_key = "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"
    
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

    response_index = max([int(f[len('response'):-4]) for f in os.listdir(RESPONSE_DIR) if f.startswith("response") and f.endswith(".txt")], default=0) + 1
    response_file = os.path.join(RESPONSE_DIR, f"response{response_index}.txt")

    with open(response_file, 'w') as file:
        file.write(response_content)

    print(f"Response saved to {response_file}")
    return response_file

def text_to_speech(response_file):
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

    with open(response_file, 'r') as file:
        input_text = file.read().strip()

    inputs = processor(text=input_text, return_tensors="pt")

    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

    output_index = max([int(f[len('output'):-4]) for f in os.listdir(OUTPUT_DIR) if f.startswith("output") and f.endswith(".mp3")], default=0) + 1
    output_file = os.path.join(OUTPUT_DIR, f"output{output_index}.mp3")
    sf.write(output_file, speech.numpy(), samplerate=16000)

    print(f"Audio saved to {output_file}")
    return output_file

def main():
    if not os.path.exists(RECORD_DIRECTORY):
        os.makedirs(RECORD_DIRECTORY)
    if not os.path.exists(TRANSCRIPTION_DIR):
        os.makedirs(TRANSCRIPTION_DIR)
    if not os.path.exists(RESPONSE_DIR):
        os.makedirs(RESPONSE_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = os.listdir(RECORD_DIRECTORY)
    index = max([int(f[5:-4]) for f in files if f.startswith("audio") and f.endswith(".mp3")], default=0) + 1
    output_filename = os.path.join(RECORD_DIRECTORY, f"audio{index}.mp3")

    # Run the pipeline
    record_audio(output_filename)
    transcription_file = transcribe_audio(output_filename)
    response_file = generate_response(transcription_file)
    audio_output_file = text_to_speech(response_file)

    # Play the final audio file
    playsound.playsound(audio_output_file)

if __name__ == "__main__":
    main()
