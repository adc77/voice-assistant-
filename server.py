import asyncio
import json
import websockets
import webrtcvad
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCIceCandidate
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from aiortc.mediastreams import AudioFrame
from pipeline import transcribe_audio, generate_response, text_to_speech
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize VAD
vad = webrtcvad.Vad(3)

class AudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        return frame

async def process_audio(track):
    audio_data = b''
    is_speech = False
    silence_count = 0
    SILENCE_THRESHOLD = 10
    FRAME_DURATION = 30  # in milliseconds

    while True:
        try:
            frame = await track.recv()
            if not isinstance(frame, AudioFrame):
                continue

            # Ensure the audio data is in the correct format for webrtcvad
            audio = frame.to_ndarray()
            audio_bytes = audio.tobytes()

            # webrtcvad requires 16-bit PCM audio
            if frame.format.bits != 16:
                logger.warning(f"Unexpected audio format: {frame.format.bits} bits")
                continue

            try:
                is_speech_frame = vad.is_speech(audio_bytes, sample_rate=frame.sample_rate)
            except Exception as e:
                logger.error(f"VAD error: {e}")
                continue

            if is_speech_frame:
                is_speech = True
                silence_count = 0
                audio_data += audio_bytes
            else:
                silence_count += 1

            if is_speech and silence_count >= SILENCE_THRESHOLD:
                try:
                    transcription = transcribe_audio(audio_data)
                    response = generate_response(transcription)
                    audio_response = text_to_speech(response)
                    
                    audio_data = b''
                    is_speech = False
                    silence_count = 0

                    return audio_response
                except Exception as e:
                    logger.error(f"Error in audio processing pipeline: {e}")
                    logger.debug(traceback.format_exc())
                    return None
        except Exception as e:
            logger.error(f"Error while processing frame: {e}")
            logger.debug(traceback.format_exc())

async def handle_audio_processing(track, websocket):
    while True:
        try:
            audio_response = await process_audio(track)
            if audio_response:
                await websocket.send(json.dumps({
                    "type": "audio",
                    "data": audio_response.decode('latin1')
                }))
                logger.info("Audio response sent to client")
        except Exception as e:
            logger.error(f"Error in audio processing: {e}")
            logger.debug(traceback.format_exc())

async def handle_connection(websocket, path):
    pc = RTCPeerConnection()
    recorder = MediaBlackhole()

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        logger.info(f"ICE connection state is {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed":
            await pc.close()

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            audio_track = AudioTrack(track)
            pc.addTrack(audio_track)
            asyncio.create_task(handle_audio_processing(audio_track, websocket))

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
                if msg["candidate"]:
                    try:
                        candidate_init = {
                            "sdpMid": msg["candidate"].get("sdpMid"),
                            "sdpMLineIndex": msg["candidate"].get("sdpMLineIndex"),
                            "candidate": msg["candidate"].get("candidate")
                        }
                        candidate = RTCIceCandidate(candidate_init)
                        await pc.addIceCandidate(candidate)
                    except Exception as e:
                        logger.error(f"Error adding ICE candidate: {e}")
                        logger.debug(traceback.format_exc())
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.debug(traceback.format_exc())
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
    logger.info("WebSocket server started on ws://localhost:8080")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())