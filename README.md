# RedOT – Red Team Toolkit for Robots and OT stuff

## Overview
RedOT is a modular offensive framework for red teaming autonomous gardener robots. It includes capabilities across:
- Wireless exploitation (BLE, RF, Wi-Fi)
- Firmware analysis and CVE-based attacks
- Hardware hacking (UART, JTAG)
- AI manipulation (adversarial visuals, voice injection)
- Covert payloads and C2 channels

---

##  Modules

### Recon
- `wifi_scan.py`: Scan local Wi-Fi for devices
- `ble_scan.py`: (Coming soon)
- `rf_sniffer.py`: (Coming soon)

### Wireless Attacks
- `wifi_attack.py`: Evil Twin attack
- `ble_crasher.py`: BLE advertisement flood
- `rf_signal_cloner.py`: Replay captured RF signals

### Firmware
- `unpack_and_analyze.sh`: Unpacks firmware images
- `cve_autopwn.py`: CVE matching from firmware strings
- `firmware_poisoner.py`: Injects payloads into firmware

### Hardware Interface
- `uart_auto_connect.py`: UART discovery
- `uart_extractor.py`: Auto-connect and dump output
- `jtag_auto_interface.py`: Simulated JTAG memory dump

### AI Attacks
- `image_spoof.py`: Overlay message on live camera
- `model_confuser.py`: Add adversarial noise to confuse AI
- `voice_injection.py`: TTS-based voice command attack

### Payloads
- `watering_loop.sh`: Simulated infinite watering
- `loop_bomb.py`: Repeating motion + watering payload
- `dns_c2.py`: Covert command beacon via DNS

### Copilot & GUI
- `recon_assistant.py`: GPT-powered suggestions (stub)
- `dashboard.py`: Flask GUI (stub)

---

##  Usage

Run the main CLI launcher:
```bash
bash redot.sh
```

Follow the menu to explore modules. All output logs saved under `logs/`.

---

## Requirements
Install with:
```bash
pip install -r requirements.txt
```

---

## Output & Logs
- Logs: `logs/`
- Reports: `reports/` (future)
- Config: `config/targets.yaml`

---

##  Status
All modules operational. real-time C2 dashboard in development.

---

##  Legal
RedOT is for **authorized red team operations only**. Use responsibly. MADE by S0m3R34P3r
