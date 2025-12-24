from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from collections import deque
import uvicorn

app = FastAPI(title="ASRS 3D Model Control API")

# CORS - localhost only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8013)
