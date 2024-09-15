# voice assistant

## Overview
This project implements a real-time audio processing server using WebSockets. It captures audio from a client, processes it to detect speech, transcribes the audio, generates a response using a language model, and converts the response to speech. The server is built using Python and leverages several libraries for audio processing, machine learning, and WebSocket communication.

## Technologies Used
- **Python**: The primary programming language for the server.
- **WebSockets**: For real-time communication between the server and clients.
- **aiortc**: A library for WebRTC and real-time communication.
- **webrtcvad**: Voice Activity Detection (VAD) to determine if audio contains speech.
- **numpy**: For numerical operations on audio data.
- **soundfile**: For reading and writing audio files.
- **gTTS (Google Text-to-Speech)**: For converting text responses to speech.
- **Groq**: For audio transcription and generating responses using a language model.
- **pyaudio**: For capturing audio input from the microphone.
- **playsound**: For playing audio files.
- **asyncio**: For asynchronous programming in Python.

## Features
- **Real-time Audio Processing**: Captures audio from clients and processes it in real-time.
- **Speech Detection**: Uses VAD to detect speech in the audio stream.
- **Transcription**: Converts audio to text using a transcription service.
- **Response Generation**: Generates a response based on the transcribed text using Llama 3 (LLM).
- **Text-to-Speech**: Converts the generated response back to audio for playback.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/adc77/voice-assistant-.git
   cd voice-assistant-
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Ensure you have the `GROQ_API_KEY` set in your environment for accessing the transcription and response generation services.

## Usage
1. Start the WebSocket server:
   ```bash
   python server.py
   ```

2. Connect a client to the server and start sending audio data.

3. The server will process the audio, transcribe it, generate a response, and send back the audio response.

## File Structure
- `server.py`: The main server file that handles WebSocket connections and audio processing.
- `pipeline.py`: Contains functions for audio recording, transcription, response generation, and text-to-speech conversion.

