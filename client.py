import requests
import datetime
from timeit import default_timer as timer

SERVER_URL = "http://prayudahlah:8000/time"


def synchronize_time():
    # Catat waktu sebelum request
    t0 = timer()

    # Kirim GET request ke server
    response = requests.get(SERVER_URL)

    # Catat waktu setelah response diterima
    t1 = timer()

    # Ambil waktu server dari JSON response
    server_data = response.json()
    server_time = datetime.datetime.fromisoformat(server_data["server_time"])

    # Hitung RTT dan waktu baru
    rtt = t1 - t0
    new_client_time = server_time + datetime.timedelta(seconds=rtt / 2)

    print(f"Waktu Server (UTC) : {server_time}")
    print(f"RTT                : {rtt:.6f} detik")
    print(f"Estimasi delay     : {rtt / 2:.6f} detik")
    print(f"Waktu Klien Baru   : {new_client_time}")

    return new_client_time


if __name__ == "__main__":
    synchronize_time()
