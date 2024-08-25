import os
import sys
sys.path.append('myenv\Lib\site-packages\groq')
from groq import Groq

# Get the API key from the environment variable
#api_key = os.getenv('GROQ_API_KEY')

api_key = "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"

# Initialize Groq client with the API key
client = Groq(api_key=api_key)

# Initialize Groq client
# client = Groq()

# Directories for input and output
TRANSCRIPTION_DIR = "transcriptions"
RESPONSE_DIR = "responses"

# Ensure the directories exist
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)
os.makedirs(RESPONSE_DIR, exist_ok=True)

# Determine the latest index based on existing files in the transcription directory
files = os.listdir(TRANSCRIPTION_DIR)
index = max([int(f[len('transcription'):-4]) for f in files if f.startswith("transcription") and f.endswith(".txt")], default=0)

# Read the content from the latest transcription file
transcription_file = os.path.join(TRANSCRIPTION_DIR, f"transcription{index}.txt")
with open(transcription_file, 'r') as file:
    user_message = file.read()

# Generate a chat completion with 35 tokens
chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "you are a concise and focused assistant."},
        {"role": "user", "content": user_message}
    ],
    model="llama3-8b-8192",
    temperature=0.2, # more deterministic
    max_tokens=40,
    top_p=0.9,
    stop=["\n"], # stop generation at a logical stopping point
    stream=False,
)

# Get the response content
response_content = chat_completion.choices[0].message.content

# Save the response to response{index}.txt
response_file = os.path.join(RESPONSE_DIR, f"response{index}.txt")
with open(response_file, 'w') as file:
    file.write(response_content)

print(f"Response saved to {response_file}")
