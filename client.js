const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const statusDiv = document.getElementById('status');

let pc;
let stream;
let ws;

startButton.onclick = start;
stopButton.onclick = stop;

async function start() {
    startButton.disabled = true;
    stopButton.disabled = false;
    statusDiv.textContent = 'Connecting...';

    try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        statusDiv.textContent = 'Got media stream. Creating WebSocket...';

        ws = new WebSocket('ws://localhost:8080');
        
        ws.onopen = async () => {
            statusDiv.textContent = 'WebSocket connected. Creating peer connection...';
            pc = new RTCPeerConnection();

            stream.getTracks().forEach(track => pc.addTrack(track, stream));

            pc.onicecandidate = e => {
                if (e.candidate) {
                    ws.send(JSON.stringify({ 
                        type: 'ice', 
                        candidate: {
                            sdpMid: e.candidate.sdpMid,
                            sdpMLineIndex: e.candidate.sdpMLineIndex,
                            foundation: e.candidate.foundation,
                            component: e.candidate.component,
                            protocol: e.candidate.protocol,
                            priority: e.candidate.priority,
                            address: e.candidate.address,
                            port: e.candidate.port,
                            type: e.candidate.type,
                            tcpType: e.candidate.tcpType
                        }
                    }));
                }
            };

            pc.ontrack = e => {
                const audio = new Audio();
                audio.srcObject = e.streams[0];
                audio.play();
            };

            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            ws.send(JSON.stringify({ 
                type: 'offer', 
                sdp: pc.localDescription.sdp 
            }));
        };

        ws.onmessage = async (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'answer') {
                await pc.setRemoteDescription(new RTCSessionDescription(message));
                statusDiv.textContent = 'Connected. Speak now.';
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            statusDiv.textContent = 'WebSocket error: ' + error.message;
        };

        ws.onclose = () => {
            statusDiv.textContent = 'WebSocket closed. Please refresh and try again.';
        };

    } catch (err) {
        console.error(err);
        statusDiv.textContent = 'Error: ' + err.message;
    }
}

function stop() {
    if (pc) {
        pc.close();
    }
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    if (ws) {
        ws.close();
    }
    startButton.disabled = false;
    stopButton.disabled = true;
    statusDiv.textContent = 'Stopped';
}