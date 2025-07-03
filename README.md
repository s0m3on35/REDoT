
# RedOT – Red Team Toolkit for Robots and OT Systems

## Overview

RedOT is a modular, fully operational toolkit designed for red teaming autonomous robots, OT/ICS systems, smart environments, and embedded devices. It includes advanced capabilities for wireless exploitation, firmware manipulation, hardware interface attacks, AI deception, covert payloads, and real-time agent control through a multi-agent dashboard.

## Core Capabilities

- Wireless exploitation: BLE spoofing, Evil Twin APs, RF replay, jamming
- Firmware: unpacking, patching, poisoning, automated CVE-based payloads
- Hardware interfaces: UART and JTAG memory extraction and firmware dumps
- AI manipulation: adversarial image injection, model confusion, TTS command injection
- Covert operations: DNS C2, AES encryption, stealth implants, persistence logic
- Web dashboard: agent control, RTSP feeds, alerts, chat-based Copilot
- GPT integration: recon planning, module chaining, kill chain generation, report creation

## Module Categories

### Recon

- `wifi_scan.py` – Wi-Fi access point and client enumeration with filters
- `ble_scan.py` – BLE advertisement parsing, vendor tagging, passive mapping
- `rf_sniffer.py` – SDR-based RF entropy logging, signal capture (.pcap/.wav)

### Wireless Attacks

- `wifi_attack.py` – Evil Twin with credential capture, implant deployment, post-ex chaining
- `ble_crasher.py` – BLE flooding with spoofed MACs and device names
- `rf_signal_cloner.py` – Real RF capture and replay with `.sub`, `.wav`, `.pcap` export

### Firmware Analysis and Exploits

- `unpack_and_analyze.sh` – Extracts embedded firmware formats and triggers CVE matching
- `firmware_poisoner.py` – Injects payloads into firmware images with integrity checks
- `cve_autopwn.py` – CVE enumeration, proof-of-concept testing, automated matching
- `uart_extractor.py` – Dumps memory, firmware, logs over UART automatically
- `jtag_auto_interface.py` – Dumps full binary image over JTAG, detects and uploads implants

### Hardware Interface Attacks

- `uart_auto_connect.py` – Detects UART interfaces across baud rates
- `jtag_auto_interface.py` – Reads memory segments, supports flash dump
- `relay_attack_orchestrator.py` – Coordinates BLE/UWB-based relay attacks with `.pcap` export

### AI Deception and Adversarial Attacks

- `image_spoof.py` – Injects adversarial patches into live camera feeds
- `model_confuser.py` – Real-time ML classifier confusion through pixel modification
- `voice_injection.py` – Generates TTS payloads for smart speaker injection

### Payloads and C2

- `dns_c2.py` – AES-encrypted DNS C2, rotating resolvers, command queue, persistence
- `implant_dropper.py` – Persistent implant installer with dashboard callback
- `stealth_agent.py` – Covert beacon, file exfil, keylogging, crontab-based persistence
- `loop_bomb.py` – Infinite loop control across sensors/actuators via Zigbee, MQTT, HTTP
- `watering_loop.sh` – Cross-protocol irrigation hijack and actuator trigger

### Advanced Exploits and Field Attacks

- `rfid_cloner.py` – Clones RFID tags, supports Flipper-compatible `.sub` files
- `can_bus_payload_detonator.py` – Sends malicious CAN frames to automotive ECUs
- `ota_firmware_injector.py` – Intercepts OTA updates, modifies and delivers poisoned firmware
- `screen_firmware_overwriter.py` – Overwrites public screens with spoofed firmware visuals
- `broadcast_emergency_spoofer.py` – Spoofs multicast alert messages on signage networks
- `iot_led_sign_controller.py` – Injects commands into LED displays over Telnet

### Dashboard and Copilot

- `dashboard_ws_server.py` – WebSocket server powering real-time agent feeds
- `dashboard.html` – Real-time web GUI with agent list, map, controls, and alert stream
- `copilot_chat.py` – GPT-integrated command assistant for recon and chaining
- `recon_assistant.py` – Automatically generates recon sequences and filters
- `killchain_builder.py` – Maps agent activity to MITRE ATT&CK and event timeline
- `report_builder.py` – Creates detailed post-op reports with artifacts and summaries
- `rtsp_viewer.py` – Streams live camera feeds with anomaly detection overlay

## Usage

### Launch RedOT

```bash
bash redot.sh
