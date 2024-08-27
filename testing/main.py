import os
import subprocess


def run_script(script_name):
    result = subprocess.run(["python", script_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script_name}: {result.stderr}")
        return False
    print(f"{script_name} ran successfully.")
    return True

def main():
    # Step 1: Record audio and save it
    if not run_script("recording.py"):
        return

    # Step 2: Transcribe the recorded audio
    if not run_script("transcription.py"):
        return

    # Step 3: Process the transcription with an LLM
    if not run_script("llm.py"):
        return

    # Step 4: Convert the LLM response to speech
    if not run_script("text_speech.py"):
        return

    print("End-to-end pipeline completed successfully.")

if __name__ == "__main__":
    main()
