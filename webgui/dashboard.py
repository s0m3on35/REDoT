#!/usr/bin/env python3
import os
import json
from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_socketio import SocketIO, emit
from threading import Thread

app = Flask(__name__)
app.secret_key = 'redot-secure-key'
socketio = SocketIO(app)

TEMPLATE_DIR = 'webgui/templates'
STATIC_DIR = 'webgui/static'
AGENTS_JSON = 'webgui/agents.json'
AGENT_INVENTORY = 'recon/agent_inventory.json'


def ensure_templates():
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)

    templates = {
        "index.html": '''<!DOCTYPE html><html><head><title>REDOT Dashboard</title><style>body{font-family:monospace;background:#101010;color:#0f0;}</style></head><body><h1>REDOT Tactical Dashboard</h1>{% if 'logged_in' in session %}<ul><li><a href="/copilot">Copilot</a></li><li><a href="/launch">Launch Modules</a></li><li><a href="/streams">RTSP Streams</a></li><li><a href="/agents">Agent Map</a></li><li><a href="/logout">Logout</a></li></ul>{% else %}<form method="POST" action="/login"><input type="text" name="user" placeholder="Username"><input type="password" name="pwd" placeholder="Password"><button type="submit">Login</button></form>{% endif %}</body></html>''',
        "copilot.html": '''<html><body style="background:#111;color:#0f0;font-family:monospace;"><h2>Copilot</h2><pre id="copilot-log">Connecting...</pre><script>let s=new WebSocket("ws://"+location.host+"/copilot-feed");s.onmessage=(e)=>{document.getElementById("copilot-log").innerText+="\\n"+e.data;}</script></body></html>''',
        "launch.html": '''<html><body style="background:#111;color:#0f0;font-family:monospace;"><h2>Launch Module</h2><form method="POST"><select name="module">{% for mod in modules %}<option>{{mod}}</option>{% endfor %}</select><button type="submit">Launch</button></form><div class="log-box" style="background:#000;padding:10px;margin-top:10px;"></div></body></html>''',
        "streams.html": '''<html><body style="background:#111;color:#0f0;font-family:monospace;"><h2>RTSP Streams</h2><video id="stream" width="640" height="480" controls autoplay src="/static/sample_feed.mp4"></video></body></html>''',
        "agents.html": '''<html><body style="background:#111;color:#0f0;font-family:monospace;"><h2>Agent Map</h2><ul id="agent-list"></ul><script>fetch('/agents.json').then(r=>r.json()).then(data=>{let ul=document.getElementById("agent-list");data.forEach(a=>{let li=document.createElement("li");li.textContent=a.name+" @ "+a.ip;ul.appendChild(li);});});</script></body></html>'''
    }

    for name, content in templates.items():
        with open(os.path.join(TEMPLATE_DIR, name), "w") as f:
            f.write(content)


def ensure_agents_json():
    os.makedirs(os.path.dirname(AGENTS_JSON), exist_ok=True)
    if os.path.exists(AGENT_INVENTORY):
        try:
            with open(AGENT_INVENTORY) as src:
                agents = json.load(src)
                with open(AGENTS_JSON, "w") as dst:
                    json.dump(agents, dst, indent=2)
        except Exception:
            with open(AGENTS_JSON, "w") as f:
                json.dump([], f)
    elif not os.path.exists(AGENTS_JSON):
        with open(AGENTS_JSON, "w") as f:
            json.dump([], f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    if request.form["user"] == "admin" and request.form["pwd"] == "redot":
        session["logged_in"] = True
    return redirect("/")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/")


@app.route("/copilot")
def copilot():
    if 'logged_in' not in session:
        return redirect("/")
    return render_template("copilot.html")


@app.route("/copilot-feed")
def copilot_feed():
    return redirect("ws://" + request.host + "/copilot-feed")


@socketio.on("connect")
def on_connect():
    emit("message", "Connected to REDOT Copilot")


def broadcast_suggestions():
    suggestions = [
        "Use dns_c2.py for covert command channel",
        "Deploy rf_signal_cloner.py on garden perimeter",
        "Enable RTSP monitoring and motion alerts",
        "Inject automation override via dashboard_override.py"
    ]
    import time
    while True:
        for s in suggestions:
            socketio.emit("message", s)
            time.sleep(6)


@app.route("/launch", methods=["GET", "POST"])
def launch():
    if 'logged_in' not in session:
        return redirect("/")
    modules = sorted([f for f in os.listdir("modules") if f.endswith(".py")])
    if request.method == "POST":
        mod = request.form["module"]
        os.system(f"python3 modules/{mod} > webgui/static/last_run.txt &")
    return render_template("launch.html", modules=modules)


@app.route("/streams")
def streams():
    return render_template("streams.html")


@app.route("/agents")
def agents():
    return render_template("agents.html")


@app.route("/agents.json")
def agent_data():
    if not os.path.exists(AGENTS_JSON):
        return json.dumps([])
    with open(AGENTS_JSON) as f:
        return f.read()


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


if __name__ == "__main__":
    ensure_templates()
    ensure_agents_json()
    Thread(target=broadcast_suggestions, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)
