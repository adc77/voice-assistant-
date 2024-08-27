"""
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
    """