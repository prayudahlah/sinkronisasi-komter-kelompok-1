import argparse
import asyncio
import json
import signal
import sys
import time

import websockets

CLIENT_PORT = 5001


def format_time(ts):
    d = time.localtime(ts)
    ms = int((ts % 1) * 1000)
    return f"{d.tm_hour:02d}:{d.tm_min:02d}:{d.tm_sec:02d}.{ms:03d}"


class SlaveClock:
    def __init__(self, drift_rate=0.0):
        self.start_real = time.time()
        self.drift_rate = drift_rate
        self.adjustment = 0.0
        self.history = []

    def get_time(self):
        elapsed = time.time() - self.start_real
        drifted = elapsed * (1 + self.drift_rate)
        return self.start_real + drifted + self.adjustment

    def set_time(self, target_time):
        now = time.time()
        elapsed = now - self.start_real
        drifted = elapsed * (1 + self.drift_rate)
        self.adjustment = target_time - (self.start_real + drifted)


async def run(server: str, port: int, drift: float):
    clock = SlaveClock(drift_rate=drift)
    uri = f"ws://{server}/ws/client"

    print("=" * 60)
    print(" BERKELEY ALGORITHM - CLIENT NODE ".center(60, "="))
    print("=" * 60)
    print(f"  Server: {server}")
    print(f"  Port: {port}")
    print(f"  Drift rate: {drift:+.6f} detik/detik", end="")
    if drift > 0:
        print(" (jam LEBIH CEPAT)")
    elif drift < 0:
        print(" (jam LEBIH LAMBAT)")
    else:
        print(" (normal)")
    print(f"  Waktu awal: {format_time(clock.get_time())}")
    print("=" * 60)

    while True:
        try:
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps({"action": "register", "port": port}))
                print(f"\n  [REGISTER] Terdaftar di server {server}")

                async for msg in ws:
                    data = json.loads(msg)
                    command = data.get("command")

                    if command == "get_time":
                        master_time = data.get("master_time", 0)
                        t = clock.get_time()
                        offset = master_time - t
                        clock.history.append(t)
                        print(f"\n[REQUEST] Master: {format_time(master_time)} | Local: {format_time(t)} | Offset: {offset:+.4f}")
                        await ws.send(json.dumps({"time": t, "offset": offset}))

                    elif command == "set_time":
                        universal_time = data.get("universal_time", 0)
                        before = clock.get_time()
                        clock.set_time(universal_time)
                        after = clock.get_time()
                        print(f"\n[SET TIME] Universal: {format_time(universal_time)}")
                        print(f"  Sebelum: {format_time(before)} → Sesudah: {format_time(after)}")
                        await ws.send(
                            json.dumps(
                                {
                                    "status": "ok",
                                    "before": before,
                                    "after": after,
                                }
                            )
                        )

        except websockets.ConnectionClosed:
            print("\n  [WS] Koneksi terputus, reconnect dalam 3 detik...")
            await asyncio.sleep(3)
        except (OSError, ConnectionError) as e:
            print(f"\n  [WS] Gagal connect: {e}, coba lagi 3 detik...")
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Berkeley Algorithm - Client Node")
    parser.add_argument("--server", required=True, help="Alamat server (host:port)")
    parser.add_argument(
        "--drift", type=float, default=0.0, help="Drift rate (default: 0)"
    )
    parser.add_argument(
        "--port", type=int, default=5001, help="Port listener (default: 5001)"
    )
    args = parser.parse_args()

    try:
        asyncio.run(run(args.server, CLIENT_PORT, args.drift))
    except KeyboardInterrupt:
        pass
