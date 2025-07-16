#!/usr/bin/env python3
# REDoT Web Console Bootstrap Launcher

import subprocess
import sys
import os
import webbrowser
import platform
from pathlib import Path
import time
import shutil

REQUIRED_PACKAGES = [
    "flask",
    "flask_cors"
]

WEBSERVER_PATH = Path("webgui/app.py")
LAUNCH_PORT = 5050
MIN_PYTHON = (3, 7)
LOGS_DIR = Path("logs")
RESULTS_DIR = Path("results")
MODULES_DIR = Path("modules")
WEBGUI_DIR = Path("webgui")

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

def check_python_version():
    if sys.version_info < MIN_PYTHON:
        print(f"[!] Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.")
        sys.exit(1)

def install_dependencies():
    log("Checking required Python packages...")
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
            log(f"✓ {package} already installed")
        except ImportError:
            log(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def verify_structure():
    log("Verifying directory structure...")
    for d in [MODULES_DIR, LOGS_DIR, RESULTS_DIR, WEBGUI_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    if not WEBSERVER_PATH.exists():
        log(f"[!] Web server not found at: {WEBSERVER_PATH}")
        sys.exit(1)

def clear_logs():
    if LOGS_DIR.exists():
        shutil.rmtree(LOGS_DIR)
        LOGS_DIR.mkdir()
        log("Cleared old logs.")
    if RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)
        RESULTS_DIR.mkdir()
        log("Cleared old results.")

def launch_web_console():
    log(f"Launching REDoT Web Console on http://localhost:{LAUNCH_PORT} ...")
    python_exec = "python3" if platform.system() != "Windows" else "python"
    subprocess.Popen([python_exec, str(WEBSERVER_PATH)])

    time.sleep(2)

    try:
        webbrowser.open(f"http://localhost:{LAUNCH_PORT}")
        log("Web console opened in browser.")
    except Exception:
        log("[!] Could not open browser automatically. Visit http://localhost:5050 manually.")

if __name__ == "__main__":
    print("====== REDoT Web Console Bootstrap ======")
    check_python_version()
    install_dependencies()
    verify_structure()
    # clear_logs()  # Optional: uncomment if you want fresh logs every run
    launch_web_console()
