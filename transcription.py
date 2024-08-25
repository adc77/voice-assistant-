import os
from faster_whisper import WhisperModel

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# Create transcriptions directory if it doesn't exist
if not os.path.exists("transcriptions"):
    os.makedirs("transcriptions")

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