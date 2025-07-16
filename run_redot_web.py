#!/usr/bin/env python3
# REDoT Launcher: Dependency Installer + Web UI Bootstrap

import subprocess
import sys
import os
import webbrowser
import platform
from pathlib import Path
import time

REQUIRED_PACKAGES = [
    "flask",
    "flask_cors"
]

WEBSERVER_PATH = Path("webgui/app.py")
LAUNCH_PORT = 5050

def install_dependencies():
    print("[*] Checking and installing required dependencies...")
    for package in REQUIRED_PACKAGES:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def verify_structure():
    print("[*] Verifying REDoT directory structure...")
    required_dirs = ["modules", "logs", "results", "webgui"]
    for d in required_dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

    if not WEBSERVER_PATH.exists():
        print(f"[!] Web server not found at: {WEBSERVER_PATH}")
        sys.exit(1)

def launch_web_console():
    print(f"[*] Launching REDoT Web Console on http://localhost:{LAUNCH_PORT} ...")
    if platform.system() in ["Linux", "Darwin"]:
        subprocess.Popen(["python3", str(WEBSERVER_PATH)])
    else:
        subprocess.Popen(["python", str(WEBSERVER_PATH)])

    time.sleep(2)  # Wait for Flask to boot
    try:
        webbrowser.open(f"http://localhost:{LAUNCH_PORT}")
    except Exception:
        print("[!] Could not open browser automatically.")

if __name__ == "__main__":
    print("====== REDoT Web Console Bootstrap ======")
    install_dependencies()
    verify_structure()
    launch_web_console()
