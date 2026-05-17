import argparse
import json
import signal
import sys
import time
from urllib.request import Request, urlopen

from network import start_server

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

    def apply_adjustment(self, value):
        self.adjustment += value


def handle_request(data):
    command = data.get("command")

    if command == "get_time":
        current_time = clock.get_time()
        clock.history.append(current_time)
        print(f"\n[REQUEST] Diminta waktu -> {format_time(current_time)}")
        return {"time": current_time}

    elif command == "adjust":
        value = data.get("value", 0)
        before = clock.get_time()
        clock.apply_adjustment(value)
        after = clock.get_time()
        print(f"\n[ADJUSTMENT] Diterima: {value:+.4f}")
        print(f"  Waktu sebelum: {format_time(before)}")
        print(f"  Waktu sesudah: {format_time(after)}")
        print(f"  Total koreksi kumulatif: {clock.adjustment:+.4f}")
        return {"status": "ok", "before": before, "after": after}

    return {"error": "unknown command"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Berkeley Algorithm - Client Node")
    parser.add_argument("--server", help="Alamat server (host:port) untuk register")
    parser.add_argument(
        "--drift", type=float, default=0.0, help="Drift rate (default: 0)"
    )
    parser.add_argument(
        "--port", type=int, default=5001, help="Port listener (default: 5001)"
    )
    args = parser.parse_args()

    CLIENT_PORT = args.port
    clock = SlaveClock(drift_rate=args.drift)

    print("=" * 60)
    print(" BERKELEY ALGORITHM - CLIENT NODE ".center(60, "="))
    print("=" * 60)
    print(f"  Port: {CLIENT_PORT}")
    print(f"  Drift rate: {args.drift:+.6f} detik/detik", end="")
    if args.drift > 0:
        print(" (jam LEBIH CEPAT)")
    elif args.drift < 0:
        print(" (jam LEBIH LAMBAT)")
    else:
        print(" (normal)")
    if args.server:
        print(f"  Server: {args.server}")
    print(f"  Waktu awal: {format_time(clock.get_time())}")
    print("=" * 60)

    # Register ke server jika --server diberikan
    if args.server:
        data = json.dumps({"port": CLIENT_PORT}).encode()
        req = Request(
            f"http://{args.server}/api/register",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(req) as resp:
                result = json.loads(resp.read())
                if result.get("status") == "ok":
                    print(f"  [REGISTER] Terdaftar di server {args.server}")
        except Exception as e:
            print(f"  [REGISTER] Gagal: {e}")

    # Cleanup saat shutdown
    def cleanup(sig, frame):
        if args.server:
            data = json.dumps({"port": CLIENT_PORT}).encode()
            req = Request(
                f"http://{args.server}/api/unregister",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            try:
                urlopen(req)
                print(f"\n  [UNREGISTER] Dihapus dari server {args.server}")
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    start_server(CLIENT_PORT, handle_request)
