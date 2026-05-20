import asyncio
import json
import os
import platform
import subprocess
import time

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from network import send_message

# ===================== KONFIGURASI =====================

SLAVES = [
    ("nixia", 5001),  # Satria
    ("anin", 5001),  # Anin
    ("yoekesekti", 5001),  # Yoeke
    ("vioouw", 5001),  # Vio
    ("namba", 5001),  # Namba
]
INTERVAL = 10

# ===================== STATE =====================

state = {
    "running": True,
    "iteration": 0,
    "interval": INTERVAL,
    "average": 0,
    "current": {},
    "history": [],
    "slaves": SLAVES.copy(),
}

clients: set[WebSocket] = set()
ws_slaves: dict[str, WebSocket] = {}
ws_responses: dict[str, dict] = {}

# ===================== BROADCAST =====================


async def broadcast():
    if not clients:
        return
    data = json.dumps(state, default=str)
    dead = set()
    for ws in clients:
        try:
            await ws.send_text(data)
        except Exception:
            dead.add(ws)
    clients.difference_update(dead)


# ===================== HELPERS =====================


async def send_to_slave(ip: str, port: int, command: dict, timeout: int = 5):
    """Kirim command ke slave via WebSocket jika terhubung, fallback ke TCP."""
    client_id = f"{ip}:{port}"
    ws = ws_slaves.get(client_id)
    if ws:
        ws_responses.pop(client_id, None)
        try:
            await ws.send_text(json.dumps(command))
            for _ in range(timeout * 10):
                if client_id in ws_responses:
                    return ws_responses.pop(client_id)
                await asyncio.sleep(0.1)
        except Exception:
            pass
        return {"error": "ws timeout"}
    else:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, send_message, ip, port, command)


# ===================== CLOCK UTILITIES =====================


def adjust_host_clock(ts):
    """Set sistem clock host ke timestamp yang diberikan."""
    syst = platform.system()
    try:
        if syst == "Linux":
            subprocess.run(["date", "-s", f"@{ts}"], check=True, capture_output=True)
        elif syst == "Darwin":
            subprocess.run(["date", "-s", f"@{ts}"], check=True, capture_output=True)
        elif syst == "Windows":
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))
            subprocess.run(
                ["powershell", "Set-Date", f"'{dt}'"],
                check=True,
                capture_output=True,
            )
        print(f"[CLOCK] Waktu sistem diubah ke {ts} ({format_time(ts)})")
        return True
    except Exception as e:
        msg = f"[CLOCK] Gagal mengubah waktu sistem: {e}"
        print(msg)
        return False


def format_time(ts):
    d = time.localtime(ts)
    ms = int((ts % 1) * 1000)
    return f"{d.tm_hour:02d}:{d.tm_min:02d}:{d.tm_sec:02d}.{ms:03d}"


# ===================== ALGORITMA BERKELEY =====================


async def berkeley_loop():
    loop = asyncio.get_event_loop()

    while True:
        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break

        if not state["running"]:
            continue

        # === FASE 1: Kirim waktu master ke semua slave ===
        state["iteration"] += 1
        iteration = state["iteration"]
        master_time = time.time()

        tasks = []
        for ip, port in state["slaves"]:
            tasks.append(
                send_to_slave(
                    ip, port, {"command": "get_time", "master_time": master_time}
                )
            )

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # === FASE 2: Kumpulkan offset dari client ===
        offsets = {}
        for (ip, port), resp in zip(state["slaves"], responses):
            key = f"{ip}:{port}"
            if isinstance(resp, dict) and "error" not in resp and "offset" in resp:
                offsets[key] = resp["offset"]
            else:
                offsets[key] = None

        # === FASE 3: Hitung rata-rata offset ===
        valid_offsets = [o for o in offsets.values() if o is not None]
        avg_offset = (
            sum(valid_offsets) / len(valid_offsets) if valid_offsets else 0.0
        )

        # === FASE 4: Universal time ===
        universal_time = master_time + avg_offset
        state["average"] = avg_offset
        state["universal_time"] = universal_time

        # === FASE 5: Adjust host system clock ===
        clock_adjusted = adjust_host_clock(universal_time)

        # === FASE 6: Kirim universal time ke semua slave ===
        adj_tasks = []
        for name, offset in offsets.items():
            if offset is not None:
                ip, port = name.split(":")
                adj_tasks.append(
                    send_to_slave(
                        ip,
                        int(port),
                        {"command": "set_time", "universal_time": universal_time},
                    )
                )
        if adj_tasks:
            await asyncio.gather(*adj_tasks, return_exceptions=True)

        # === Update state ===
        state["calculation"] = {
            "iteration": iteration,
            "n": len(valid_offsets),
            "avg_offset": avg_offset,
            "master_time": master_time,
            "universal_time": universal_time,
            "clock_adjusted": clock_adjusted,
            "offsets": offsets.copy(),
        }

        state["current"] = {}
        state["current"]["Master"] = {
            "time": master_time,
            "offset": 0,
            "status": "online",
        }
        for name, offset in offsets.items():
            state["current"][name] = {
                "time": master_time - offset if offset is not None else None,
                "offset": offset if offset is not None else 0,
                "status": "online" if offset is not None else "offline",
            }

        state["history"].append(
            {
                "iteration": iteration,
                "data": {
                    name: {"offset": offsets[name]}
                    for name in offsets
                },
            }
        )
        if len(state["history"]) > 50:
            state["history"].pop(0)

        # === Broadcast ke frontend ===
        await broadcast()

        # === Tunggu interval ===
        remaining = state["interval"]
        while remaining > 0:
            if not state["running"]:
                break
            await asyncio.sleep(0.1)
            remaining -= 0.1


# ===================== FASTAPI APP =====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(berkeley_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/register")
async def register(data: dict, request: Request):
    ip = data.get("ip", request.client.host)
    port = data.get("port", 5001)
    slave = (ip, port)
    if slave not in state["slaves"]:
        state["slaves"].append(slave)
    await broadcast()
    return {"status": "ok", "slaves": state["slaves"]}


@app.post("/api/unregister")
async def unregister(data: dict):
    ip = data.get("ip")
    port = data.get("port", 5001)
    state["slaves"] = [s for s in state["slaves"] if s != (ip, port)]
    await broadcast()
    return {"status": "ok"}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    # Kirim state terkini segera setelah connect
    await websocket.send_text(json.dumps(state, default=str))
    try:
        while True:
            data = await websocket.receive_text()
            cmd = json.loads(data)
            action = cmd.get("action")

            if action == "start":
                state["running"] = True
            elif action == "stop":
                state["running"] = False
            elif action == "set_interval":
                val = cmd.get("value", 10)
                state["interval"] = max(1, val)

            await broadcast()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS ERROR] {type(e).__name__}: {e}")
    finally:
        clients.discard(websocket)


@app.websocket("/ws/client")
async def ws_client(websocket: WebSocket):
    await websocket.accept()

    try:
        data = await websocket.receive_text()
        msg = json.loads(data)
        ip = websocket.client.host
        port = msg.get("port", 5001)
        client_id = f"{ip}:{port}"
        ws_slaves[client_id] = websocket

        if (ip, port) not in state["slaves"]:
            state["slaves"].append((ip, port))
            await broadcast()

        print(f"[WS CLIENT] {client_id} terdaftar")

        while True:
            data = await websocket.receive_text()
            ws_responses[client_id] = json.loads(data)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS CLIENT ERROR] {e}")
    finally:
        ws_slaves.pop(client_id, None)
        ws_responses.pop(client_id, None)
        print(f"[WS CLIENT] {client_id} terputus")


# Serve frontend (React build)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
