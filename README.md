
# RedOT – Red Team Toolkit for Robots and OT Systems

## Overview

RedOT is a modular, fully operational toolkit designed for red teaming autonomous robots, OT/ICS systems, and smart environments. It includes advanced capabilities for wireless exploitation, firmware manipulation, hardware interface attacks, AI deception, covert payloads, and real-time control via a multi-agent dashboard.

## Core Features

- Wireless attacks: BLE spoofing, RF replay, Evil Twin with implant injection
- Firmware unpacking, payload poisoning, and CVE-based exploitation
- UART and JTAG hardware interfaces with auto extraction and binary dumping
- AI manipulation: adversarial images, TTS command injection, spoofed sensors
- Covert communication: DNS C2 with AES, Tor proxy, and persistence logic
- Real-time dashboard with agent control, alert feed, and integrated Copilot
- GPT-assisted module chaining, report generation, and post-execution automation

## Modules

### Recon
- `wifi_scan.py`: Wi-Fi scanning with filtering and enrichment
- `ble_scan.py`: BLE beacon and vendor discovery
- `rf_sniffer.py`: RF analysis with entropy visualization and `.pcap` export

### Wireless Attacks
- `wifi_attack.py`: Evil Twin with credential capture, implant dropper, auto post-execution
- `ble_crasher.py`: BLE flooding, spoofed device IDs, multi-interface support
- `rf_signal_cloner.py`: RF capture and replay with .sub/.wav/.pcap generation

### Firmware Analysis
- `unpack_and_analyze.sh`: Unpacks firmware and auto-triggers follow-up modules
- `firmware_poisoner.py`: Injects payloads with reverse shell and dashboard alerts
- `cve_autopwn.py`: Extracts CVEs from firmware for automated exploitation
- Fully chained with `uart_extractor.py`, dashboard auto-actions, and Metasploit

### Hardware Interface
- `uart_auto_connect.py`: Detects active UART devices
- `uart_extractor.py`: Dumps memory, logs, and firmware from UART
- `jtag_auto_interface.py`: Extracts memory and binaries via JTAG interface

### AI Attacks
- `image_spoof.py`: Overlays adversarial patterns on camera feeds
- `model_confuser.py`: Confuses AI classifiers using pattern injection
- `voice_injection.py`: Injects commands via generated TTS audio

### Payloads and Command & Control
- `watering_loop.sh`: Triggers actuator logic across Zigbee, MQTT, HTTP, and RF
- `loop_bomb.py`: Loops commands across actuators with persistence options
- `dns_c2.py`: AES-encrypted DNS-based covert channel with exfil and command queue
- `implant_dropper.py`: Deploys persistent implant to victim system
- `stealth_agent.py`: Covert beaconing agent with file exfil, persistence, and keylogger

### Copilot and Dashboard
- `dashboard_ws_server.py`: WebSocket server powering real-time UI
- `dashboard.html`: HTML-based UI for agent control and event visualization
- `copilot_chat.py`: GPT-powered command assistant with chain logic
- `recon_assistant.py`: GPT-driven recon planning module
- `killchain_builder.py`: Maps live events to MITRE and timelines
- `report_builder.py`: Generates structured output reports with full artifacts
- `rtsp_viewer.py`: Monitors live camera feeds for anomalies

## Usage

### Launch CLI interface
```bash
bash redot.sh
