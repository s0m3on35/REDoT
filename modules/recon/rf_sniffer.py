#!/usr/bin/env python3

import subprocess
import argparse
import json
import datetime
import os

LOG_DIR = "logs/rf_sniffer"
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def run_rf_sniffer(freq, rate, duration, logfile):
    log(f"RF Sniffer started: {freq} MHz for {duration} sec")
    cmd = ["rtl_433", "-f", f"{freq}M", "-s", str(rate), "-F", f"json:{logfile}", "-T", str(duration)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        for line in proc.stdout:
            try:
                signal = json.loads(line.strip())
                log(f"{signal.get('frequency', freq*1e6)/1e6} MHz | {signal.get('model', 'Unknown')} | {json.dumps(signal.get('data', {}))}")
            except json.JSONDecodeError:
                continue
    except KeyboardInterrupt:
        log("Sniffer stopped")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--frequency", type=float, default=433.92)
    parser.add_argument("-s", "--sample-rate", type=int, default=1024)
    parser.add_argument("-d", "--duration", type=int, default=300)
    parser.add_argument("-o", "--output", type=str, default=f"{LOG_DIR}/rf_log.json")
    args = parser.parse_args()
    run_rf_sniffer(args.frequency, args.sample_rate*1000, args.duration, args.output)

if __name__ == "__main__":
    main()
