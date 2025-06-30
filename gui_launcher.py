import os
import subprocess
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

MODULES = {
    "WiFi Scan": "modules/recon/wifi_scan.py",
    "BLE Scan": "modules/recon/ble_scan.py",
    "RF Sniffer": "modules/recon/rf_sniffer.py",
    "Evil Twin": "wifi_attack.py",
    "Implant Dropper": "implant_dropper.py",
    "Stealth Agent": "modules/stealth_agent.py",
    "Intel Enricher": "modules/intel_enricher.py",
    "GPT Copilot": "modules/gpt_live_copilot.py",
    "Killchain Builder": "modules/killchain_builder.py",
    "Report Generator": "modules/report_builder.py",
    "RTSP Viewer": "modules/rtsp_viewer.py",
    "Firmware Poisoner": "modules/firmware/firmware_poisoner.py",
    "Firmware Unpack": "modules/firmware/unpack_and_analyze.sh"
}

class RedOTGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("REDOT GUI Launcher")
        layout = QVBoxLayout()
        for name, path in MODULES.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, p=path: self.launch(p))
            layout.addWidget(btn)
        self.setLayout(layout)

    def launch(self, script_path):
        if script_path.endswith(".sh"):
            subprocess.Popen(["bash", script_path])
        else:
            subprocess.Popen(["python3", script_path])

if __name__ == "__main__":
    app = QApplication([])
    window = RedOTGUI()
    window.show()
    app.exec_()
