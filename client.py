import requests
import datetime
from timeit import default_timer as timer

SERVER_URL = "http://prayudahlah:8001/time"


def format_utc(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def synchronize_time():
    # Catat waktu sebelum request
    t0 = timer()
    client_time_before = datetime.datetime.utcnow()

    # Kirim GET request ke server
    response = requests.get(SERVER_URL)

    # Catat waktu setelah response diterima
    t1 = timer()
    client_time_after = datetime.datetime.utcnow()

    # Ambil waktu server dari JSON response
    server_data = response.json()
    server_time = datetime.datetime.fromisoformat(server_data["server_time"])

    # Hitung RTT dan waktu baru
    rtt = t1 - t0
    new_client_time = server_time + datetime.timedelta(seconds=rtt / 2)

    print("Christian's Algorithm")
    print(f"T0 (Client Send)   : {format_utc(client_time_before)}")
    print(f"T1 (Client Recv)   : {format_utc(client_time_after)}")
    print(f"T_server (UTC)     : {format_utc(server_time)}")
    print(f"RTT = T1 - T0      : {rtt:.6f} detik")
    print(f"Offset = RTT/2     : {rtt / 2:.6f} detik")
    print(f"T_client_new       : {format_utc(new_client_time)}")

    return new_client_time


if __name__ == "__main__":
    synchronize_time()
