import asyncio
import json
import os
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Lightweight RFID event relay so the frontend can react in real-time.
# The expectation is that an RFID reader (USB HID wedge, serial daemon, etc.)
# sends POST requests to /api/rfid/scan. The frontend subscribes to
# /api/rfid/stream via Server-Sent Events (SSE) to get notified immediately.

app = FastAPI(title="RFID Event Bridge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RfidScan(BaseModel):
    tag: str
    source: Optional[str] = None  # e.g. "hid_keyboard", "serial_daemon", etc.


# Each connected client gets an asyncio.Queue to receive broadcasted scans
listeners: List[asyncio.Queue] = []

# Map known tags to specific boxes (box_1 - box_5)
TAG_TO_BOX = {
    "0000000001": "box_1",
    "0000000002": "box_2",
    "0000000003": "box_3",
    "0000000004": "box_4",
    "0000000005": "box_5",
}

STATE_FILE = Path(os.getenv("RFID_STATE_FILE", "data/rfid_state.json"))


def load_box_states() -> Dict[str, str]:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            if isinstance(data, dict):
                return {k: ("Out" if v == "Out" else "In") for k, v in data.items()}
        except Exception:
            pass
    return {box: "In" for box in TAG_TO_BOX.values()}


def persist_box_states(states: Dict[str, str]) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(states))
    except Exception as exc:
        print(f"Warning: failed to persist RFID state: {exc}")


# Authoritative state for the first five boxes
box_states: Dict[str, str] = load_box_states()


async def broadcast_scan(data: Dict):
    """Send the scan payload to all connected SSE listeners."""
    stale_listeners = []
    for queue in listeners:
        try:
            queue.put_nowait(data)
        except asyncio.QueueFull:
            stale_listeners.append(queue)

    # Clean up any listeners that failed
    for queue in stale_listeners:
        if queue in listeners:
            listeners.remove(queue)


def format_sse(data: Dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/rfid/scan")
async def post_scan(scan: RfidScan):
    """Entry point for the RFID reader daemon or simulator."""
    tag = scan.tag.strip()
    payload = build_payload_from_tag(tag, scan.source or "unknown")
    await broadcast_scan(payload)
    return {"received": True, "box": payload.get("box"), "action": payload.get("action")}


@app.post("/api/rfid/mock-scan")
async def mock_scan(tag: str = "0000000001"):
    """Simple helper endpoint to fire an event without real hardware."""
    payload = build_payload_from_tag(tag.strip(), "mock")
    await broadcast_scan(payload)
    return {"broadcasted": True, "box": payload.get("box"), "action": payload.get("action")}


@app.get("/api/rfid/stream")
async def stream() -> StreamingResponse:
    """
    SSE endpoint for the frontend. Keeps an open connection and pushes each scan.
    """
    queue: asyncio.Queue = asyncio.Queue()
    listeners.append(queue)

    async def event_generator() -> AsyncIterator[str]:
        try:
            while True:
                data = await queue.get()
                yield format_sse(data)
        except asyncio.CancelledError:
            # Client disconnected
            pass
        finally:
            if queue in listeners:
                listeners.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/rfid/state")
async def state():
    """Expose current authoritative state for mapped boxes."""
    return {"boxes": box_states}


def build_payload_from_tag(tag: str, source: str) -> Dict:
    """
    Determine which box this tag maps to and toggle its state.
    Returns a payload ready to broadcast to listeners.
    """
    box_name = TAG_TO_BOX.get(tag)
    if not box_name:
        return {"tag": tag, "source": source, "recognized": False}

    # Toggle state: In -> Out, Out -> In
    current = box_states.get(box_name, "In")
    next_state = "Out" if current == "In" else "In"
    box_states[box_name] = next_state
    persist_box_states(box_states)
    action = "out" if next_state == "Out" else "in"

    return {
        "tag": tag,
        "source": source,
        "recognized": True,
        "box": box_name,
        "action": action,
        "status": next_state,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app_rfid:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
    )
