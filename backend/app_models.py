from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, List
from collections import deque
import uvicorn
import asyncio
import socket
import threading
import queue
import time

app = FastAPI(title="ASRS 3D Model Control API")

# CORS - allow all origins for cross-device communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket clients for hand detection events
hand_detection_clients: List[WebSocket] = []

# WebSocket clients for video streaming
video_clients: List[WebSocket] = []

# WebSocket clients for QC video streaming
qc_video_clients: List[WebSocket] = []

# UDP Video Bridge Configuration
UDP_IP = "0.0.0.0"
UDP_PORT = 9999
MAX_DGRAM = 65507

# UDP Control Signal Configuration
CONTROL_UDP_PORT = 9998

# QC Video Stream Configuration
QC_UDP_PORT = 9997
qc_latest_frame = None
qc_frame_lock = threading.Lock()

# Frame queue for video streaming
frame_queue = queue.Queue(maxsize=2)
latest_frame = None
frame_lock = threading.Lock()

# Event loop reference for thread communication
main_loop = None

# Window visibility state
window_visible = False

# Command queue for frontend to poll
command_queue = deque()

# Request Model - actions match Svelte function names exactly
class ExecuteActionRequest(BaseModel):
    boxId: str
    action: Literal[
        "MoveArmToBoxInitialPosition",
        "moveBoxOutOfShelf",
        "moveBoxAndArmToOutput",
        "moveBoxToOutput",
        "MoveBoxOutOfASRS",
        "moveBoxToInput",
        "moveBoxFromInputToArm",
        "moveArmToInput",
        "moveBoxAndArmToBoxPosition",
        "putBoxOnShelf"
    ]

class BoxIdRequest(BaseModel):
    boxId: str

# Sequence for getting a box out of ASRS
GET_BOX_OUT_SEQUENCE = [
    "MoveArmToBoxInitialPosition",
    "moveBoxOutOfShelf",
    "moveBoxAndArmToOutput",
    "moveBoxToOutput",
    "MoveBoxOutOfASRS",
    "moveBoxToInput",
]

@app.post("/api/models/get-box-out")
async def get_box_out(request: BoxIdRequest):
    """Queue the full sequence to get a box out of ASRS"""
    for action in GET_BOX_OUT_SEQUENCE:
        command_queue.append({
            "boxId": request.boxId,
            "action": action
        })
    return {
        "status": "queued",
        "boxId": request.boxId,
        "sequence": GET_BOX_OUT_SEQUENCE,
        "queueLength": len(command_queue)
    }

@app.post("/api/models/execute-action")
async def execute_action(request: ExecuteActionRequest):
    """Queue an action for frontend to execute"""
    command_queue.append({
        "boxId": request.boxId,
        "action": request.action
    })
    return {
        "status": "queued",
        "boxId": request.boxId,
        "action": request.action,
        "queueLength": len(command_queue)
    }

@app.get("/api/models/pending-command")
async def get_pending_command():
    """Frontend polls this endpoint to get next command"""
    if command_queue:
        command = command_queue.popleft()
        return {"hasCommand": True, "command": command}
    return {"hasCommand": False, "command": None}

# WebSocket endpoint for frontend to receive hand detection events
@app.websocket("/ws/hand-detection")
async def websocket_hand_detection(websocket: WebSocket):
    await websocket.accept()
    hand_detection_clients.append(websocket)

    # If window is already visible, notify this new client immediately
    if window_visible:
        await websocket.send_json({"event": "hand_detected"})
        print("New client connected - window already visible, triggering popup")

    try:
        while True:
            msg = await websocket.receive_text()
            # Respond to ping with pong to keep connection alive
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        if websocket in hand_detection_clients:
            hand_detection_clients.remove(websocket)
    except Exception:
        if websocket in hand_detection_clients:
            hand_detection_clients.remove(websocket)


# Endpoint called by model PC when hand is detected
@app.post("/api/hand-detected")
async def hand_detected():
    """Called by the model PC when hand is detected - notifies all connected frontends"""
    for client in hand_detection_clients:
        try:
            await client.send_json({"event": "hand_detected"})
        except:
            pass  # Client disconnected
    return {"status": "ok", "notified_clients": len(hand_detection_clients)}


# Endpoint called by model PC when hand is removed
@app.post("/api/hand-removed")
async def hand_removed():
    """Called by the model PC when hand is no longer detected - notifies all connected frontends"""
    for client in hand_detection_clients:
        try:
            await client.send_json({"event": "hand_removed"})
        except:
            pass  # Client disconnected
    return {"status": "ok", "notified_clients": len(hand_detection_clients)}


# WebSocket endpoint for video streaming to frontend
@app.websocket("/ws/video")
async def websocket_video(websocket: WebSocket):
    global latest_frame
    await websocket.accept()
    video_clients.append(websocket)
    print(f"Video client connected. Total: {len(video_clients)}")

    try:
        frame_count = 0
        while True:
            # Get latest frame
            with frame_lock:
                current_frame = latest_frame

            # Only send if we have a frame AND window is visible
            if current_frame is not None and window_visible:
                await websocket.send_bytes(current_frame)
                frame_count += 1
                if frame_count % 100 == 0:
                    print(f"Sent {frame_count} frames to client")

            # ~30 FPS
            await asyncio.sleep(0.033)
    except WebSocketDisconnect:
        if websocket in video_clients:
            video_clients.remove(websocket)
        print("Video client disconnected")
    except Exception as e:
        if websocket in video_clients:
            video_clients.remove(websocket)
        print(f"Video WebSocket error: {e}")


# WebSocket endpoint for QC video streaming to frontend
@app.websocket("/ws/qc-video")
async def websocket_qc_video(websocket: WebSocket):
    global qc_latest_frame
    try:
        await websocket.accept()
        qc_video_clients.append(websocket)
        print(f"QC video client connected. Total: {len(qc_video_clients)}")

        frame_count = 0
        while True:
            # Get latest QC frame
            with qc_frame_lock:
                current_frame = qc_latest_frame

            # Send if we have a frame (always on, no visibility check)
            if current_frame is not None:
                await websocket.send_bytes(current_frame)
                frame_count += 1
                if frame_count % 100 == 0:
                    print(f"Sent {frame_count} QC frames to client")

            # ~30 FPS
            await asyncio.sleep(0.033)
    except WebSocketDisconnect:
        if websocket in qc_video_clients:
            qc_video_clients.remove(websocket)
        print("QC video client disconnected")
    except Exception as e:
        if websocket in qc_video_clients:
            qc_video_clients.remove(websocket)
        print(f"QC video WebSocket error: {e}")


def control_signal_receiver_thread():
    """Background thread that receives control signals (DETECTED/REMOVED)"""
    global window_visible

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, CONTROL_UDP_PORT))
    print(f"UDP Control Signal Receiver Started on port {CONTROL_UDP_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            signal = data.decode('utf-8').strip()
            print(f"Received control signal: {signal} from {addr}")

            if signal == "DETECTED":
                # Show window
                if not window_visible:
                    window_visible = True
                    print("Window now visible - triggering popup")

                    # Notify all hand detection clients
                    if main_loop:
                        for client in list(hand_detection_clients):
                            try:
                                asyncio.run_coroutine_threadsafe(
                                    client.send_json({"event": "hand_detected"}),
                                    main_loop
                                )
                            except Exception as e:
                                print(f"Error notifying client: {e}")

            elif signal == "REMOVED":
                # Hide window immediately
                if window_visible:
                    window_visible = False
                    print("Hiding window immediately")

                    # Notify all hand detection clients
                    if main_loop:
                        for client in list(hand_detection_clients):
                            try:
                                asyncio.run_coroutine_threadsafe(
                                    client.send_json({"event": "hand_removed"}),
                                    main_loop
                                )
                            except Exception as e:
                                print(f"Error notifying client: {e}")

        except Exception as e:
            print(f"Control Signal UDP Error: {e}")


def udp_receiver_thread():
    """Background thread that receives UDP frames"""
    global latest_frame
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"UDP Video Bridge Started on port {UDP_PORT}")

    frame_count = 0

    while True:
        try:
            data, addr = sock.recvfrom(MAX_DGRAM)

            with frame_lock:
                latest_frame = data

            frame_count += 1

            if frame_count % 100 == 0:
                print(f"Received {frame_count} UDP frames from {addr}")

        except Exception as e:
            print(f"UDP Error: {e}")


def qc_udp_receiver_thread():
    """Background thread that receives QC crack detection video frames"""
    global qc_latest_frame
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, QC_UDP_PORT))
    print(f"QC Video Bridge Started on port {QC_UDP_PORT}")

    frame_count = 0

    while True:
        try:
            data, addr = sock.recvfrom(MAX_DGRAM)

            with qc_frame_lock:
                qc_latest_frame = data

            frame_count += 1

            if frame_count % 100 == 0:
                print(f"Received {frame_count} QC UDP frames from {addr}")

        except Exception as e:
            print(f"QC UDP Error: {e}")


@app.on_event("startup")
async def startup_event():
    """Start UDP receiver threads when FastAPI starts"""
    global main_loop
    main_loop = asyncio.get_running_loop()

    # Start video frame receiver thread
    video_thread = threading.Thread(target=udp_receiver_thread, daemon=True)
    video_thread.start()
    print("Video bridge thread started")

    # Start control signal receiver thread
    control_thread = threading.Thread(target=control_signal_receiver_thread, daemon=True)
    control_thread.start()
    print("Control signal receiver thread started")

    # Start QC video receiver thread
    qc_video_thread = threading.Thread(target=qc_udp_receiver_thread, daemon=True)
    qc_video_thread.start()
    print("QC video receiver thread started")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8013)  # 0.0.0.0 to allow external connections
