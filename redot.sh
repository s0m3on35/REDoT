#!/bin/bash
echo "🧠 REDOT - Unified Red Team Toolkit for Gardener Robots"
PS3='Select an operation: '
options=("Recon" "Wireless Attacks" "Hardware Interface" "AI Attacks" "Firmware Analysis" "Deploy Payload" "Launch Copilot" "Camera Spoofing" "Exit")
select opt in "${options[@]}"
            python3 copilot/copilot_engine.py  # [Laptop, GPT]
do
    case $opt in
        "Recon")
            python3 modules/recon/wifi_scan.py  # [Laptop Wi-Fi (Monitor Mode)]
            python3 modules/wireless/ble_crasher.py  # [Flipper, RPi BLE Dongle]
            python3 modules/wireless/rf_signal_cloner.py  # [HackRF, RTL-SDR]
            python3 modules/firmware/cve_autopwn.py  # [Laptop]
            python3 modules/firmware/firmware_poisoner.py  # [Laptop]
            python3 modules/ai_attacks/model_confuser.py  # [Webcam, RPi]
            python3 modules/ai_attacks/voice_injection.py  # [Laptop Speaker, RPi Audio]
            python3 modules/hardware/uart_extractor.py  # [FTDI UART, RPi]
            python3 modules/hardware/jtag_auto_interface.py  # [Bus Pirate, JTAGulator]
            python3 modules/payloads/loop_bomb.py  # [MQTT, UART]
            python3 modules/payloads/dns_c2.py  # [Laptop, Internet]
            ;;
        "Wireless Attacks")
            python3 modules/wireless/wifi_attack.py  # [Alfa Wi-Fi Adapter]
            python3 modules/wireless/ble_crasher.py  # [Flipper, RPi BLE Dongle]
            python3 modules/wireless/rf_signal_cloner.py  # [HackRF, RTL-SDR]
            ;;
        "Hardware Interface")
            python3 modules/hardware/uart_auto_connect.py  # [RPi, FTDI UART Adapter]
            python3 modules/hardware/uart_extractor.py  # [FTDI UART, RPi]
            python3 modules/hardware/jtag_auto_interface.py  # [Bus Pirate, JTAGulator]
            ;;
        "AI Attacks")
            python3 modules/ai_attacks/image_spoof.py  # [Webcam, RPi]
            python3 modules/ai_attacks/model_confuser.py  # [Webcam, RPi]
            python3 modules/ai_attacks/voice_injection.py  # [Laptop Speaker, RPi Audio]
            ;;
        "Firmware Analysis")
            bash modules/firmware/unpack_and_analyze.sh  # [None]
            python3 modules/firmware/cve_autopwn.py  # [Laptop]
            python3 modules/firmware/firmware_poisoner.py  # [Laptop]
            ;;
        "Deploy Payload")
            bash modules/payloads/watering_loop.sh  # [MQTT Access]
            python3 modules/payloads/loop_bomb.py  # [MQTT, UART]
            python3 modules/payloads/dns_c2.py  # [Laptop, Internet]
            ;;
        "Launch Copilot")
            python3 copilot/recon_assistant.py  # [Laptop, GPT]
            ;;
        "Camera Spoofing")
            python3 modules/ai_attacks/cam_spoof.py
            ;;
        "Exit")
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done

# IoT/OT Attack Modules

echo "📡 OT/IoT Attacks:"
PS3='Select OT/IoT operation: '
iot_options=("Camera Hijack [IP Cam, ONVIF]" "Access Control Replay [RFID, Flipper, Proxmark]" "Back" "HVAC Fuzzer [BACnet/Modbus]" "Dashboard Override [Home Assistant]" )
select iot_opt in "${iot_options[@]}"
do
    case $iot_opt in
        "HVAC Fuzzer [BACnet/Modbus]")
            python3 modules/iot/hvac_fuzzer.py
            ;;
        "Dashboard Override [Home Assistant]")
            python3 modules/iot/dashboard_override.py
            ;;
        "Camera Hijack [IP Cam, ONVIF]")
            python3 modules/iot/cam_hijack.py
            ;;
        "Access Control Replay [RFID, Flipper, Proxmark]")
            python3 modules/iot/access_replay.py
            ;;
        "Back")
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done

# Report Generator

echo "📝 Reporting:"
python3 modules/report_builder.py  # [Laptop]

# AI & Camera Expansion

echo "🤖 Copilot Tools:"
python3 modules/copilot_chat.py  # [Laptop, GPT]

echo "📹 Camera Tools:"
python3 modules/rtsp_viewer.py  # [Laptop, RTSP cam]

echo "🕵️ Persistence & Callback:"
python3 modules/stealth_agent.py  # [Target, Cron/Webhook]

# AI & Threat Mapping

echo "🧠 AI Ops:"
python3 modules/gpt_live_copilot.py  # [Laptop, GPT API]
python3 modules/intel_enricher.py  # [Laptop, Internet]
python3 modules/killchain_builder.py  # [Laptop, Report]
