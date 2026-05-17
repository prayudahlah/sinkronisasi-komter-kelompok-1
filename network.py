import socket
import json


def send_message(ip, port, data):
    """Kirim data JSON ke IP:port, return response"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        sock.send(json.dumps(data).encode())
        response = sock.recv(1024).decode()
        sock.close()
        return json.loads(response)
    except Exception as e:
        return {"error": str(e)}


def start_server(port, callback):
    """Mulai server, panggil callback(data) untuk setiap request"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"[SERVER] Listening on port {port}")

    while True:
        conn, addr = server.accept()
        data = json.loads(conn.recv(1024).decode())
        response = callback(data)
        conn.send(json.dumps(response).encode())
        conn.close()
