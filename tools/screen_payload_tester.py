# tools/screen_payload_tester.py

import argparse
import numpy as np
from PIL import Image
import os
import time

def raw_rgb565_to_image(data, width=320, height=240):
    arr = np.frombuffer(data, dtype=np.uint16).reshape((height, width))
    r = ((arr >> 11) & 0x1F) << 3
    g = ((arr >> 5) & 0x3F) << 2
    b = (arr & 0x1F) << 3
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(rgb, 'RGB')

def preview_static(bin_path):
    with open(bin_path, "rb") as f:
        data = f.read()
    img = raw_rgb565_to_image(data)
    img.show(title="Preview - Static")

def preview_animated(bin_path, width=320, height=240, delay=0.1):
    frame_size = width * height * 2
    with open(bin_path, "rb") as f:
        data = f.read()

    total_frames = len(data) // frame_size
    print(f"[+] Detected {total_frames} animation frames")

    for i in range(total_frames):
        frame_data = data[i * frame_size : (i + 1) * frame_size]
        img = raw_rgb565_to_image(frame_data)
        img.show(title=f"Frame {i+1}/{total_frames}")
        time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description="Screen Payload Tester (RGB565 Preview)")
    parser.add_argument("--bin", required=True, help="Path to .bin visual payload")
    parser.add_argument("--animated", action="store_true", help="Preview as animated sequence")
    parser.add_argument("--delay", type=float, default=0.2, help="Frame delay for animation preview")
    args = parser.parse_args()

    if args.animated:
        preview_animated(args.bin, delay=args.delay)
    else:
        preview_static(args.bin)

if __name__ == "__main__":
    main()
