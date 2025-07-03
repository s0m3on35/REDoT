#!/usr/bin/env python3
# gui_launcher.py - REDOT Enhanced GUI Launcher (clean version)

import os
import subprocess
import yaml
import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QScrollArea, QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGETS_FILE = os.path.join(BASE_DIR, "config", "targets.yaml")
MODULE_FOLDERS = [
    "modules/recon", "modules/wireless", "modules/firmware",
    "modules/attacks", "modules/exploits", "modules/payloads"
]
POST_CHAIN_MODULE = os.path.join(BASE_DIR, "modules/payloads/post/implant_dropper.py")

# Optional WebSocket alert system
try:
    from webgui.dashboard_ws_client import send_alert
except ImportError:
    def send_alert(msg): pass  # Fallback if client not found

class RedOTGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("REDOT GUI Launcher")
        self.resize(700, 800)
        self.module_map = self.discover_modules()
        self.filtered_map = self.module_map.copy()

        layout = QVBoxLayout()

        # Target selection
        layout.addWidget(QLabel("Select Target"))
        self.target_dropdown = QComboBox()
        self.load_targets()
        layout.addWidget(self.target_dropdown)

        # Category filter
        layout.addWidget(QLabel("Filter by Module Type"))
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItem("All")
        self.category_dropdown.addItems(sorted(set(k.split(" → ")[0] for k in self.module_map)))
        self.category_dropdown.currentIndexChanged.connect(self.filter_modules)
        layout.addWidget(self.category_dropdown)

        # Search bar
        layout.addWidget(QLabel("Search Modules"))
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.filter_modules)
        layout.addWidget(self.search_box)

        # Module list
        self.scroll_area = QScrollArea()
        self.module_widget = QWidget()
        self.module_layout = QVBoxLayout()
        self.update_module_buttons()
        self.module_widget.setLayout(self.module_layout)
        self.scroll_area.setWidget(self.module_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Execution log
        layout.addWidget(QLabel("Execution Log"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def load_targets(self):
        if os.path.exists(TARGETS_FILE):
            with open(TARGETS_FILE, 'r') as f:
                targets = yaml.safe_load(f)
                for name in targets:
                    self.target_dropdown.addItem(name)

    def discover_modules(self):
        modules = {}
        for folder in MODULE_FOLDERS:
            full_path = os.path.join(BASE_DIR, folder)
            if not os.path.isdir(full_path):
                continue
            for f in sorted(os.listdir(full_path)):
                if f.endswith(".py") or f.endswith(".sh"):
                    abs_path = os.path.join(full_path, f)
                    category = folder.split("/")[-1].capitalize()
                    mod_id = f"{category} → {f}"
                    description = self.extract_doc(abs_path)
                    modules[mod_id] = {"path": abs_path, "desc": description}
        return modules

    def extract_doc(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.match(r'["\']{3}(.*)["\']{3}', line)
                    if match:
                        return match.group(1).strip()
                    if '"""' in line or "'''" in line:
                        return line.strip().strip('"\'')
        except Exception:
            pass
        return "No description"

    def update_module_buttons(self):
        for i in reversed(range(self.module_layout.count())):
            self.module_layout.itemAt(i).widget().deleteLater()

        for name, info in self.filtered_map.items():
            btn = QPushButton(f"{name}\nDescription: {info['desc']}")
            btn.clicked.connect(lambda _, p=info["path"]: self.launch(p))
            self.module_layout.addWidget(btn)

    def filter_modules(self):
        query = self.search_box.text().lower()
        category = self.category_dropdown.currentText()
        self.filtered_map = {}
        for name, data in self.module_map.items():
            if category != "All" and not name.startswith(category):
                continue
            if query in name.lower() or query in data["desc"].lower():
                self.filtered_map[name] = data
        self.update_module_buttons()

    def launch(self, script_path):
        target = self.target_dropdown.currentText()
        self.log_output.append(f"\n[RUNNING] {os.path.basename(script_path)} on target: {target}")
        send_alert(f"[ALERT] Launch: {os.path.basename(script_path)} on {target}")

        env = os.environ.copy()
        env["REDOT_TARGET"] = target
        try:
            if script_path.endswith(".sh"):
                proc = subprocess.Popen(["bash", script_path],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                proc = subprocess.Popen(["python3", script_path],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)

            for line in proc.stdout:
                self.log_output.append(line.decode(errors="ignore"))
            self.log_output.append(f"[FINISHED] {os.path.basename(script_path)}")

            if os.path.exists(POST_CHAIN_MODULE):
                self.log_output.append(f"[CHAIN] Running post-exploitation module: implant_dropper.py")
                send_alert(f"[CHAIN] Post-exploitation: implant_dropper.py on {target}")
                subprocess.Popen(["python3", POST_CHAIN_MODULE], env=env)

        except Exception as e:
            self.log_output.append(f"[ERROR] Failed to execute {script_path}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedOTGUI()
    window.show()
    sys.exit(app.exec_())
