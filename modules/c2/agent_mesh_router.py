# modules/c2/agent_mesh_router.py

import argparse
import socket
import threading
import json
import os
from datetime import datetime

ROUTER_PORT = 40404
PEER_LIST = []
LOG_PATH = "results/mesh_router_log.json"

def log_event(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def broadcast_to_peers(msg, origin=None):
    for peer in PEER_LIST:
        if peer != origin:
            try:
                s = socket.socket()
                s.connect(peer)
                s.sendall(msg.encode())
                s.close()
            except:
                pass

def handle_client(conn, addr):
    peer = (addr[0], ROUTER_PORT)
    if peer not in PEER_LIST:
        PEER_LIST.append(peer)

    msg = conn.recv(4096).decode()
    print(f"[+] Received from {addr}: {msg}")
    log_event({
        "timestamp": datetime.utcnow().isoformat(),
        "from": addr[0],
        "msg": msg
    })

    broadcast_to_peers(msg, origin=peer)
    conn.close()

def start_router(host='0.0.0.0'):
    s = socket.socket()
    s.bind((host, ROUTER_PORT))
    s.listen(10)
    print(f"[✓] Mesh router listening on {host}:{ROUTER_PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Mesh Router for REDoT")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host IP")
    args = parser.parse_args()
    start_router(args.host)
