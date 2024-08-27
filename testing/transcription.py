import os
from faster_whisper import WhisperModel
from groq import Groq

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# Create transcriptions directory if it doesn't exist
if not os.path.exists("transcriptions"):
    os.makedirs("transcriptions")


"""
model_size = "large-v3"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

audio_file = r"recordings/audio1.mp3"
segments, info = model.transcribe(audio_file, beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

segments, _ = model.transcribe(
    audio_file,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
)
segments = list(segments)  # The transcription will actually run here.

# Save transcription to a file
transcription_index = 1  # Start indexing from 1
transcription_file = f"transcriptions/transcription{transcription_index}.txt"

with open(transcription_file, "w") as f:
    for segment in segments:
        f.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n")

print(f"Transcription saved to {transcription_file}")
"""

api_key = os.getenv('GROQ_API_KEY')

 # Initialize the Groq client -- groq approach for transcription!
client = Groq(api_key=api_key)

    # Open the audio file
with open(audio_file, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=(audio_file, file.read()),  # Required audio file
            model="distil-whisper-large-v3-en",  # Required model to use for transcription
            prompt="",  # Optional context or spelling prompt
            response_format="text",  # Optional format of the response
            language="en",  # Optional language
            temperature=0.0  # Optional temperature for transcription creativity
        )
    
    # Find the next available transcription index
transcription_index = max(
        [
            int(f[len('transcription'):-4])
            for f in os.listdir(TRANSCRIPTION_DIR)
            if f.startswith("transcription") and f.endswith(".txt")
        ],
        default=0
    ) + 1
    
    # Save the transcription to a text file
transcription_file = os.path.join(TRANSCRIPTION_DIR, f"transcription{transcription_index}.txt")
with open(transcription_file, "w") as f:
        f.write(transcription.text)
    
print(f"Transcription saved to {transcription_file}")
# return transcription_file