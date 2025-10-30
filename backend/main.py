from __future__ import annotations

import json
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Device Status Service", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DeviceStore = Dict[str, Dict[str, Any]]

devices: DeviceStore = {
    "CV1": {
        "id": "CV1",
        "name": "Conveyor_Unit _1",
        "image_key": "conveyor_real",
        "subcomponents": [
            {
                "id": "SM1",
                "name": "Stepper Motor 57x56mm",
                "status": "farooq",
                "image_key": "stepper_motor",
            },
            {
                "id": "PS1",
                "name": "Proximity Sensor",
                "status": "Running",
                "image_key": "proximity_sensor",
            },
            {
                "id": "PS2",
                "name": "Proximity Sensor",
                "status": "Running",
                "image_key": "proximity_sensor",
            },
            {
                "id": "JO1",
                "name": "Jetson Orin Nano",
                "status": "Live",
                "image_key": "jetson_orin",
            },
            {
                "id": "GD1",
                "name": "Greartisan DC 24V",
                "status": "Online",
                "image_key": "dc_motor",
            },
        ],
    },
    "CV1B": {
        "id": "CV1B",
        "name": "Conveyor_Unit _1",
        "image_key": "conveyor_partial",
        "subcomponents": [
            {
                "id": "SM2",
                "name": "Stepper Motor 57x56mm",
                "status": "Running",
                "image_key": "stepper_motor",
            },
            {
                "id": "GD1",
                "name": "Greartisan DC 24V",
                "status": "Idle",
                "image_key": "dc_motor",
            },
            {
                "id": "PS3",
                "name": "Proximity Sensor",
                "status": "Running",
                "image_key": "proximity_sensor",
            },
        ],
    },
    "CV2": {
        "id": "CV2",
        "name": "Conveyor_Unit _2",
        "image_key": "conveyor_empty",
        "subcomponents": [
            {
                "id": "SM3",
                "name": "Stepper Motor 57x56mm",
                "status": "Off",
                "image_key": "stepper_motor",
            },
            {
                "id": "PS4",
                "name": "Proximity Sensor",
                "status": "Idle",
                "image_key": "proximity_sensor",
            },
        ],
    },
}


class ConnectionManager:
    def __init__(self) -> None:
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)
        await self._send_snapshot(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, payload: Dict[str, Any]) -> None:
        if not self.active:
            return

        message = json.dumps(payload)
        disconnected: List[WebSocket] = []
        for socket in self.active:
            try:
                await socket.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(socket)

        for socket in disconnected:
            self.disconnect(socket)

    async def _send_snapshot(self, websocket: WebSocket) -> None:
        snapshot = {"type": "snapshot", "payload": {"units": list(devices.values())}}
        await websocket.send_text(json.dumps(snapshot))


manager = ConnectionManager()


class StatusUpdate(BaseModel):
    unitId: str
    componentId: str
    status: str


@app.get("/api/status")
async def get_status() -> Dict[str, Any]:
    return {"units": list(devices.values())}


async def update_device_status(unit_id: str, component_id: str, new_status: str) -> Dict[str, Any]:
    unit = devices.get(unit_id)
    if unit is None:
        raise ValueError(f"Unit {unit_id} not found")

    component = next((c for c in unit["subcomponents"] if c["id"] == component_id), None)
    if component is None:
        raise ValueError(f"Component {component_id} not found in unit {unit_id}")

    component["status"] = new_status
    payload = {
        "type": "update",
        "payload": {
            "unitId": unit_id,
            "componentId": component_id,
            "id": component_id,
            "status": new_status,
        },
    }

    await manager.broadcast(payload)
    return payload["payload"]


@app.post("/api/status")
async def post_status(update: StatusUpdate) -> Dict[str, Any]:
    try:
        updated = await update_device_status(update.unitId, update.componentId, update.status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"updated": updated}


@app.get("/api/dev/flip")
async def dev_flip(unit: str = "CV1", comp: str = "SM1", to: str = "Off"):
    await update_device_status(unit, comp, to)
    return {"ok": True, "unit": unit, "component": comp, "status": to}


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
