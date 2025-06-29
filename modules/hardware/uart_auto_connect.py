#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import time
import os
import re

BAUD_RATES = [9600, 19200, 38400, 57600, 115200, 230400, 460800]
COMMON_USERNAMES = ["admin", "root", "user"]
COMMON_PASSWORDS = ["admin", "root", "1234", "toor"]
TIMEOUT = 2
LOG_DIR = "logs/uart"
DASHBOARD_LOG = "webgui/static/uart_discovery.log"
os.makedirs(LOG_DIR, exist_ok=True)

def list_uart_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def fingerprint_protocol(data):
    text = data.decode(errors="ignore").lower()
    if "login" in text or "username" in text:
        return "Login Prompt"
    if "linux" in text or "ubuntu" in text:
        return "Linux Shell"
    if "boot" in text or "u-boot" in text:
        return "Bootloader (U-Boot?)"
    if "at" in text and "ok" in text:
        return "Modem AT Commands"
    return "Unknown"

def brute_force_credentials(port, baudrate):
    try:
        with serial.Serial(port, baudrate, timeout=3) as ser:
            for user in COMMON_USERNAMES:
                for pwd in COMMON_PASSWORDS:
                    creds = f"{user}\n{pwd}\n"
                    ser.write(creds.encode())
                    time.sleep(1)
                    if ser.in_waiting:
                        resp = ser.read(ser.in_waiting)
                        if b"welcome" in resp.lower() or b"last login" in resp.lower():
                            return user, pwd
    except Exception:
        pass
    return None, None

def try_baudrate(port, baudrate):
    try:
        with serial.Serial(port, baudrate, timeout=TIMEOUT) as ser:
            time.sleep(1)
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                if data:
                    fingerprint = fingerprint_protocol(data)
                    log_file = os.path.join(LOG_DIR, f"{port.replace('/', '_')}_{baudrate}.log")
                    with open(log_file, "wb") as f:
                        f.write(data)
                    with open(DASHBOARD_LOG, "a") as dash:
                        dash.write(f"[UART] Found on {port} @ {baudrate} - {fingerprint}\n")

                    print(f"[+] Data received on {port} @ {baudrate}. Saved to {log_file}")
                    print(f"[~] Fingerprint: {fingerprint}")

                    creds = brute_force_credentials(port, baudrate)
                    if creds[0]:
                        print(f"[â] Credentials found: {creds[0]} / {creds[1]}")
                        with open(DASHBOARD_LOG, "a") as dash:
                            dash.write(f"[UART] Brute-force success: {creds[0]} / {creds[1]}\n")

                    return True
    except Exception:
        pass
    return False

def scan_uart_interfaces():
    ports = list_uart_ports()
    if not ports:
        print("[-] No UART interfaces found.")
        return

    for port in ports:
        print(f"[*] Scanning {port}...")
        for baud in BAUD_RATES:
            print(f"  ââ Trying baudrate {baud}...")
            if try_baudrate(port, baud):
                print(f"[â] Active UART found: {port} @ {baud}")
                break
        else:
            print(f"[-] No valid baudrate response from {port}")

if __name__ == "__main__":
    print("=== REDOT UART Auto Connect ===")
    scan_uart_interfaces()
