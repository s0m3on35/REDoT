# modules/payloads/screen_payload_builder.py

import argparse
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imageio
import tempfile
from datetime import datetime
import json

OUTPUT_DIR = "results/generated_firmware/"
LOG_PATH = "results/payload_builder_logs.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("results", exist_ok=True)

def log_payload(entry):
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def image_to_raw_rgb565(image):
    img = image.convert('RGB')
    arr = np.array(img)
    r = (arr[:, :, 0] >> 3).astype(np.uint16)
    g = (arr[:, :, 1] >> 2).astype(np.uint16)
    b = (arr[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.tobytes()

def generate_static_screen(output_name, input_image):
    img = Image.open(input_image).resize((320, 240))  # common screen size
    raw_data = image_to_raw_rgb565(img)
    out_path = os.path.join(OUTPUT_DIR, f"{output_name}.bin")
    with open(out_path, "wb") as f:
        f.write(raw_data)
    print(f"[✓] Static screen payload generated: {out_path}")
    return out_path

def generate_fake_error_screen(output_name, text="Firmware Error", code="ERR_0xC0DE"):
    img = Image.new("RGB", (320, 240), "black")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 90), text, fill="red", font=font)
    draw.text((10, 130), code, fill="white", font=font)
    out_path = os.path.join(OUTPUT_DIR, f"{output_name}_error.bin")
    raw_data = image_to_raw_rgb565(img)
    with open(out_path, "wb") as f:
        f.write(raw_data)
    print(f"[✓] Fake error screen payload created: {out_path}")
    return out_path

def generate_gif_animation(output_name, gif_path):
    reader = imageio.get_reader(gif_path)
    all_frames = []
    for frame in reader:
        img = Image.fromarray(frame).resize((320, 240)).convert("RGB")
        all_frames.append(image_to_raw_rgb565(img))

    bin_path = os.path.join(OUTPUT_DIR, f"{output_name}_anim.bin")
    with open(bin_path, "wb") as f:
        for frame_data in all_frames:
            f.write(frame_data)
    print(f"[✓] Animated screen payload created: {bin_path}")
    return bin_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visual Payload Generator for Screen Firmware")
    parser.add_argument("--mode", required=True, choices=["static", "error", "gif"], help="Payload mode")
    parser.add_argument("--input", help="Input image or GIF path (if required)")
    parser.add_argument("--text", help="Custom error message text (for error mode)")
    parser.add_argument("--code", help="Custom error code (for error mode)")
    parser.add_argument("--output", default="visual_payload", help="Output file prefix")
    args = parser.parse_args()

    ts = datetime.utcnow().isoformat()

    if args.mode == "static" and args.input:
        result = generate_static_screen(args.output, args.input)
    elif args.mode == "gif" and args.input:
        result = generate_gif_animation(args.output, args.input)
    elif args.mode == "error":
        result = generate_fake_error_screen(args.output, args.text or "Critical Failure", args.code or "ERR_X001")
    else:
        raise ValueError("Invalid argument combination")

    log_payload({
        "timestamp": ts,
        "mode": args.mode,
        "output": result,
        "input": args.input or "generated"
    })
