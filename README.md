# REDoT – Red Team Operations Toolkit

REDoT is a fully operational red teaming framework targeting smart environments, IoT/OT systems, embedded devices, RF protocols, and more. It includes exploit modules, reconnaissance tools, AI-driven assistants, dashboard interfaces, and post-exploitation payloads.

## Overview

REDoT is an offensive cybersecurity framework. Modules support advanced protocols (Modbus, CAN, Zigbee, BLE, JTAG, UART), custom payloads, stealth C2, real-time dashboard integration, and automated chaining logic.

## Directory Structure

config/  
└─ device_map.yaml, targets.yaml  
copilot/  
└─ recon_assistant.py, copilot_engine.py  
data/captive_portal/  
└─ index.html, login.php, creds.txt  
modules/  
├─ ai_attacks/  
├─ analysis/  
├─ attacks/  
├─ c2/  
├─ exfil/  
├─ exploits/  
├─ firmware/  
├─ hardware/  
├─ iot/  
├─ orchestration/  
├─ payloads/  
├─ pivot/  
├─ post/  
├─ recon/  
├─ simulation/  
└─ wireless/  
results/  
tools/  
utils/  
webgui/  

## Core Launchers

- redot.sh – Primary launcher (auto-detects modules)
- gui_launcher.py – GUI interface with live module selection
- launcher.sh – Shell-based starter script

## Capabilities by Category

Category | Description  
-------- | -----------  
Recon | BLE, Wi-Fi, RF, SDR, Zigbee, CAN scans  
Exploitation | CVE-based payloads, overflow scripts, brute-force  
Hardware Attacks | UART, JTAG, I2C, EEPROM, EDID tampering  
Firmware Tools | Injectors, droppers, scramblers, unpackers  
AI Engines | Copilot suggestions, auto chaining, smart targeting  
C2 / Stealth | DNS C2, loop bombs, persistence injectors  
Visual Payloads | Camera spoofing, public screen hijacks  
Web GUI | RTSP viewer, dashboard live metrics, AI chat  
Pivoting | SOCKS, UPnP punchers, MQTT hijacks  
Simulation | Replay mode, dummy triggers for testing  
Reporting | STIX exports, killchain builder, timeline reports  

## Getting Started

### Dependencies

Make sure you have:

- Python 3.8+
- aircrack-ng, hostapd, dnsmasq (for wireless modules)
- rtl-sdr, gnuradio (for RF/SDR modules)
- flask, websockets, PyYAML, rich, aiohttp, scapy

For the full list, see `requirements.txt`

## Installation

```bash
chmod +x redot.sh
./redot.sh
```

Or run:

```bash
python3 gui_launcher.py
```

## Auto-Updating Readme

To update the README with newly added modules:

```bash
python3 tools/readme_autoupdate.py
```

This will scan the modules directory and regenerate the module section automatically.

## Configuration Files

- config/device_map.yaml: Maps each module to its required hardware
- config/targets.yaml: Lists scanned or added targets for chaining
- copilot/recon_assistant.py: Copilot AI suggestions based on recon
- tools/update_module_device_map.py: Auto-injects new entries in device_map.yaml

## License

This toolkit is for authorized red teaming engagements only. All usage must comply with local and international cybersecurity laws.
