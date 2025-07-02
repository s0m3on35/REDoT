# modules/attacks/hdmi_screen_spoofer.py

import os
import argparse
import time
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

LOG_PATH = "results/hdmi_spoof_logs.json"
MITRE_TTP = "T1491.001"

def log_attack(payload):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(payload)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def generate_fake_screen(output_path, message, width=1920, height=1080):
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((width // 2 - 100, height // 2), message, font=font, fill=(255, 0, 0))
    img.save(output_path)

def push_to_display(img_path):
    os.system(f"fbi -T 1 --noverbose -a {img_path}")

def execute(message, spoof_file):
    generate_fake_screen(spoof_file, message)
    push_to_display(spoof_file)
    log_attack({
        "timestamp": datetime.utcnow().isoformat(),
        "payload": spoof_file,
        "message": message,
        "ttp": MITRE_TTP,
        "success": True
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof HDMI display with fake screen")
    parser.add_argument("--message", required=True, help="Message to display")
    parser.add_argument("--output", default="results/fake_hdmi_screen.png", help="Output image file")
    args = parser.parse_args()
    execute(args.message, args.output)
