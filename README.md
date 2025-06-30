# RedOT – Red Team Toolkit for Robots and OT Systems

## Overview

RedOT is a modular offensive framework for red teaming autonomous gardener robots and operational technology (OT) systems. It includes capabilities for:

- Wireless exploitation: BLE, RF, Evil Twin attacks
- Firmware analysis and automated CVE-based exploitation
- Hardware interface attacks: UART, JTAG memory dumping
- AI adversarial manipulation and sensor spoofing
- Covert payloads, implants, and command-and-control over DNS
- Real-time dashboard, multi-agent control, and GPT-based Copilot modules

---

## Modules

### Recon
- wifi_scan.py: Wi-Fi AP and client scanner
- ble_scan.py: BLE scanner (planned)
- rf_sniffer.py: RF signal analyzer (planned)

### Wireless Attacks
- wifi_attack.py: Evil Twin attack with captive portal, credential logger, and implant deployment
- ble_crasher.py: BLE advertisement flood and spoofing with multi-interface support
- rf_signal_cloner.py: SDR-based RF replay with entropy analysis, .sub/.wav export

### Firmware Analysis
- unpack_and_analyze.sh: Firmware unpacking via binwalk
- cve_autopwn.py: CVE matching and auto-exploit suggestion from firmware strings
- firmware_poisoner.py: Payload injection and firmware config tampering

### Hardware Interface
- uart_auto_connect.py: UART auto-detection
- uart_extractor.py: UART output dump and device interaction
- jtag_auto_interface.py: JTAG detection and memory extraction

### AI Attacks
- image_spoof.py: Adversarial overlay injection on camera feeds
- model_confuser.py: Adds adversarial noise to fool AI models
- voice_injection.py: TTS-generated voice command injection attacks

### Payloads and C2
- watering_loop.sh: Timed watering loop with MQTT, HTTP, Zigbee, and RF triggers
- loop_bomb.py: Persistent actuator/motor loop bomb
- dns_c2.py: AES-encrypted DNS-based covert channel with file transfer
- implant_dropper.py: Deploys a stealthy agent with persistence and callback
- stealth_agent.py: Persistent implant with encrypted callbacks, Tor proxy, and keylogging

### Copilot and Dashboard
- dashboard_ws_server.py: Real-time WebSocket dashboard with multi-agent command control
- recon_assistant.py: GPT-based recon planner
- copilot_chat.py: GPT-based analyst chat interface
- rtsp_viewer.py: Mask detection and live video anomaly spotting
- intel_enricher.py: Auto-query Shodan, Censys, and external OSINT sources
- killchain_builder.py: Builds attack chains and MITRE mappings from live agent data
- report_builder.py: Generates HTML and markdown reports with embedded results

---

## Usage

Launch the main interactive CLI:

```bash
bash redot.sh
