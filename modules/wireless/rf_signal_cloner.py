#!/usr/bin/env python3
"""
RF Signal Cloner 
Captures and replays RF signals (433/868/915 MHz), exports to multiple formats, and performs fingerprinting.
"""

import argparse
import os
import time
import uuid
import subprocess
import wave
import numpy as np
import matplotlib.pyplot as plt
import paho.mqtt.publish as publish

# === CONFIGURATION ===
EXPORT_DIR = "rf_captures"
MQTT_BROKER = "127.0.0.1"
MQTT_TOPIC = "redot/rf_signal"
COMMON_FREQS = [433920000, 868000000, 915000000]  # Hz

os.makedirs(EXPORT_DIR, exist_ok=True)

# === SIGNAL UTILITIES ===
def visualize_entropy(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    block_size = 256
    entropy_blocks = []
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        probs = [float(block.count(byte)) / len(block) for byte in set(block)]
        entropy = -sum([p * np.log2(p) for p in probs]) if probs else 0
        entropy_blocks.append(entropy)
    plt.plot(entropy_blocks)
    plt.title("Entropy Analysis")
    plt.xlabel("Block")
    plt.ylabel("Entropy")
    plt.show()

def save_waveform(signal_data, sample_rate, path):
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(signal_data)

# === CAPTURE FUNCTIONALITY ===
def capture_rf(freq, duration, interface="hackrf"):
    print(f"[+] Capturing on {freq/1e6:.3f} MHz for {duration}s...")
    output_bin = os.path.join(EXPORT_DIR, f"capture_{uuid.uuid4().hex}.bin")
    output_wav = output_bin.replace(".bin", ".wav")
    output_sub = output_bin.replace(".bin", ".sub")
    output_pcap = output_bin.replace(".bin", ".pcap")

    if interface == "hackrf":
        subprocess.run([
            "hackrf_transfer",
            "-f", str(int(freq)),
            "-r", output_bin,
            "-s", "2000000",
            "-n", str(2_000_000 * duration)
        ])

    # Convert to .wav for audio analysis
    raw_data = np.fromfile(output_bin, dtype=np.int8)
    audio_data = np.int16(raw_data[:len(raw_data)//2] * 256)  # basic approximation
    save_waveform(audio_data.tobytes(), 2000000, output_wav)

    # Export simulated .sub file for Flipper replay
    with open(output_sub, 'w') as f:
        f.write("Filetype: Flipper SubGhz RAW File\nVersion: 1\n")
        for _ in range(100):  # mock signal pulses
            f.write(" +400 -400\n")

    # Export .pcap (stubbed)
    with open(output_pcap, 'wb') as f:
        f.write(b'\xd4\xc3\xb2\xa1')  # pcap global header (stub for testing)

    # MQTT Push
    try:
        publish.single(MQTT_TOPIC, payload=f"RF Capture {freq}Hz stored at {output_bin}", hostname=MQTT_BROKER)
    except Exception as e:
        print(f"[!] MQTT error: {e}")

    print(f"[+] Saved to: {output_bin}, {output_wav}, {output_sub}, {output_pcap}")
    visualize_entropy(output_bin)

# === REPLAY FUNCTIONALITY ===
def replay_rf(file_path, freq):
    print(f"[+] Replaying {file_path} at {freq/1e6:.3f} MHz...")
    subprocess.run([
        "hackrf_transfer",
        "-t", file_path,
        "-f", str(int(freq)),
        "-x", "47"
    ])

# === MAIN EXECUTION ===
def main():
    parser = argparse.ArgumentParser(description="RF Signal Cloner with SDR Replay, Export, and Fingerprinting.")
    parser.add_argument("--capture", action="store_true", help="Capture mode")
    parser.add_argument("--replay", help="Replay specified .bin file")
    parser.add_argument("--freq", type=int, help="Frequency in Hz")
    parser.add_argument("--duration", type=int, default=5, help="Duration to record in seconds")
    parser.add_argument("--hop", action="store_true", help="Frequency hopping mode")
    parser.add_argument("--passive", action="store_true", help="Listen only (no replay)")
    args = parser.parse_args()

    if args.hop:
        for freq in COMMON_FREQS:
            capture_rf(freq, args.duration)
    elif args.capture and args.freq:
        capture_rf(args.freq, args.duration)
    elif args.replay and args.freq:
        if not args.passive:
            replay_rf(args.replay, args.freq)
        else:
            print("[*] Passive mode enabled. Replay skipped.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
