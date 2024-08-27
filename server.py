import asyncio
import json
import websockets
import webrtcvad
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from pipeline import transcribe_audio, generate_response, text_to_speech

# Initialize VAD
vad = webrtcvad.Vad(3)  # Aggressiveness level 3

class AudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, track):
        super().__init__()
        self.track = track
        self.buffer = []

    async def recv(self):
        frame = await self.track.recv()
        self.buffer.append(frame)
        return frame

async def process_audio(track):
    audio_data = b''
    is_speech = False
    silence_count = 0
    SILENCE_THRESHOLD = 10  # Number of silent frames before processing

    while True:
        frame = await track.recv()
        chunk = frame.to_ndarray().tobytes()
        
        # Check for speech
        if vad.is_speech(chunk, sample_rate=48000):
            is_speech = True
            silence_count = 0
            audio_data += chunk
        else:
            silence_count += 1

        if is_speech and silence_count >= SILENCE_THRESHOLD:
            # Process the collected audio
            transcription = transcribe_audio(audio_data)
            response = generate_response(transcription)
            audio_response = text_to_speech(response)
            
            # Reset for next utterance
            audio_data = b''
            is_speech = False
            silence_count = 0

            # Return the audio response
            return audio_response

async def handle_audio_processing(track):
    while True:
        try:
            audio_response = await process_audio(track)
            if audio_response:
                # Here you would send the audio_response back to the client
                # For now, we'll just print it
                print("Audio response generated")
        except Exception as e:
            print(f"Error processing audio: {e}")

async def handle_connection(websocket, path):
    pc = RTCPeerConnection()
    recorder = MediaBlackhole()

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            audio_track = AudioTrack(track)
            pc.addTrack(audio_track)
            asyncio.create_task(handle_audio_processing(audio_track))

    try:
        async for message in websocket:
            msg = json.loads(message)
            if msg["type"] == "offer":
                offer = RTCSessionDescription(sdp=msg["sdp"], type="offer")
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await websocket.send(json.dumps({
                    "type": "answer",
                    "sdp": pc.localDescription.sdp,
                }))
            elif msg["type"] == "ice":
                candidate = json.loads(msg["candidate"])
                await pc.addIceCandidate(candidate)
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")
    finally:
        await recorder.stop()
        await pc.close()

async def main():
    server = await websockets.serve(
        handle_connection, 
        "localhost", 
        8080, 
        ping_interval=None,
        ping_timeout=None
    )
    print("WebSocket server started on ws://localhost:8080")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())