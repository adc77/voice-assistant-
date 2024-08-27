import os
import torch
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset

# Initialize the processor, model, and vocoder
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# Directories for input and output
RESPONSE_DIR = "responses"
OUTPUT_DIR = "output"

# Ensure the directories exist
os.makedirs(RESPONSE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Determine the latest index based on existing files in the transcription directory
files = os.listdir(RESPONSE_DIR)
index = max([int(f[len('response'):-4]) for f in files if f.startswith("response") and f.endswith(".txt")], default=0)

# Read the content from the latest transcription file
transcription_file = os.path.join(RESPONSE_DIR, f"response{index}.txt")
with open(transcription_file, 'r') as file:
    input_text = file.read().strip()

# Process the input text
inputs = processor(text=input_text, return_tensors="pt")

# Load xvector containing speaker's voice characteristics from a dataset
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

# Generate the speech
speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

# Save the generated speech as output{index}.mp3
output_file = os.path.join(OUTPUT_DIR, f"output{index}.mp3")
sf.write(output_file, speech.numpy(), samplerate=16000)

print(f"Audio saved to {output_file}")
