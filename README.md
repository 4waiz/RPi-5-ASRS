# Digital twin dashboard (FastAPI + Svelte)

The project is now split into two folders so the backend (FastAPI) and the frontend (Svelte/Vite) can be developed and deployed independently.

```
.
├── backend/          # FastAPI app with REST + WebSocket endpoints
└── frontend/         # Svelte UI that consumes the backend through fetch + WebSocket
```

The Svelte frontend fetches `/api/status` once on load and listens to `/ws/status` for live updates, so hardware changes stream straight into the drawer without refreshing.

## Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

What you get:

| Endpoint | Description |
| --- | --- |
| `GET /api/status` | Returns the full list of conveyor units, their subcomponents, and the latest status for each item. |
| `POST /api/status` | Accepts `{ "unitId": "...", "componentId": "...", "status": "..." }` and broadcasts the change (handy for tests or other services). |
| `WS /ws/status` | Streams JSON frames such as `{ "type": "update", "payload": { "componentId": "SM1", "status": "Off" } }` every time `update_device_status()` runs. |

### Updating a real device

Whenever your PLC/robot/python script detects a change you have two options:

1. **If the code runs inside the FastAPI process** (e.g., another route or background task), import and await the helper:

```python
from backend.main import update_device_status
import asyncio

async def set_motor_off():
    await update_device_status("CV1", "SM1", "Off")

asyncio.run(set_motor_off())
```

2. **If the code runs in another process or on a different machine**, call the REST endpoint instead:

```bash
curl -X POST http://localhost:8000/api/status \
  -H "Content-Type: application/json" \
  -d "{\"unitId\":\"CV1\",\"componentId\":\"SM1\",\"status\":\"Off\"}"
```

Every connected browser that has the Svelte dashboard open will reflect the update with no refresh.

### Fake simulator (for local demos only)

There is a background task in `backend/main.py` that can randomly flip statuses so you can verify the live wiring without touching real hardware.

```powershell
cd backend
$env:ENABLE_STATUS_SIMULATOR = "1"   # enable for this terminal session
uvicorn main:app --reload --port 8000
```

As soon as the server starts, the simulator begins emitting changes through the same WebSocket channel the frontend already consumes. Remove the environment variable (or close the terminal) before deploying for real hardware, otherwise random statuses will keep overwriting your live readings.

## Frontend (Svelte + Vite)

```bash
cd frontend
npm install          # only needed the first time
npm run dev
```

The Vite dev server runs on http://localhost:5173 and automatically connects to the FastAPI backend on http://localhost:8000. If your backend lives elsewhere, set `VITE_STATUS_API` before running Vite (for example `VITE_STATUS_API=https://prod.example.com npm run dev`).

### How the live updates work

1. `src/stores/statusStore.js` fetches `GET /api/status` once to populate the UI when the page loads.
2. The same store opens `ws://localhost:8000/ws/status` and reacts to `{ type: "snapshot" }` / `{ type: "update" }` frames from FastAPI.
3. `src/components/Home-tab-pages/compunents-overview-tab.svelte` subscribes to that store. Selecting a unit opens `RightDrawer.svelte`, and the circled status text updates automatically because the drawer’s `items` prop is bound directly to the store.

### Manual end-to-end test

1. Start the backend (`uvicorn main:app --reload --port 8000`).
2. Start the frontend (`npm run dev`) and open http://localhost:5173.
3. In a new terminal run:

   ```bash
   curl -X POST http://localhost:8000/api/status \
     -H "Content-Type: application/json" \
     -d "{\"unitId\":\"CV1\",\"componentId\":\"SM1\",\"status\":\"Off\"}"
   ```

   or use PowerShell:

   ```powershell
   Invoke-RestMethod -Uri http://localhost:8000/api/status -Method Post `
     -ContentType "application/json" `
     -Body '{"unitId":"CV1","componentId":"SM1","status":"Off"}'
   ```

   The “Stepper Motor 57x56mm” line in the drawer flips to “Off” immediately while the list stays open.

4. (Optional) Set `ENABLE_STATUS_SIMULATOR=1` before launching `uvicorn` to watch the dashboard animate through random statuses, then unset it when you are done.

That’s all you need to work on real hardware events and demo fake updates without touching the UI code. Need to customise device metadata or add sensors? Update the `devices` dictionary in `backend/main.py` and the Svelte store will pull the new structure automatically on reload.
