# dashboard.py - Web Dashboard Shell
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head><title>RedOT Dashboard</title></head>
<body style="font-family:monospace;">
<h1>🖥️ RedOT Live Dashboard</h1>
<ul>
  <li><a href="/copilot">Run Copilot Engine</a></li>
  <li><a href="/launch">Launch Module</a> (coming soon)</li>
</ul>
</body>
</html>
""") 

@app.route("/copilot")
def copilot():
    return "<pre> Copilot Suggestion:\n- Use 'dns_c2.py' for covert C2.\n- Run 'loop_bomb.py' on gardenbot-01.local</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
