#!/bin/bash
# REDOT Master Launcher  

REDOT_DIR="$(dirname "$0")"
LOG_DIR="$REDOT_DIR/logs"
mkdir -p "$LOG_DIR" "$REDOT_DIR/reports" "$REDOT_DIR/results" "$REDOT_DIR/firmware"

HEADLESS=0
[[ "$1" == "--cli" ]] && HEADLESS=1

DASHBOARD_STARTED=0

main_menu() {
  clear
  echo "=== REDOT - Unified Red Team Toolkit ==="
  echo "1) Recon Modules"
  echo "2) Wireless Attacks"
  echo "3) Hardware Interface"
  echo "4) AI Attacks"
  echo "5) Firmware Analysis"
  echo "6) Deploy Payloads"
  echo "7) IoT/OT Attacks"
  echo "8) Dashboard & Copilot"
  echo "9) Reporting & Threat Intel"
  echo "10) Exit"
  echo -n "Select an option [1-10]: "
}

ensure_dashboard_running() {
  if [ "$DASHBOARD_STARTED" -eq 0 ]; then
    echo "[*] Launching WebSocket Dashboard Server..."
    python3 "$REDOT_DIR/dashboard_ws_server.py" >> "$LOG_DIR/ws_server.log" 2>&1 &
    DASHBOARD_STARTED=1
  fi
}

recon_menu() {
  echo "--- Recon ---"
  select opt in "WiFi Scan" "BLE Scan" "RF Sniffer" "Back"; do
    case $opt in
      "WiFi Scan") python3 "$REDOT_DIR/modules/recon/wifi_scan.py" | tee "$LOG_DIR/wifi_scan.log";;
      "BLE Scan") python3 "$REDOT_DIR/modules/recon/ble_scan.py" | tee "$LOG_DIR/ble_scan.log";;
      "RF Sniffer") python3 "$REDOT_DIR/modules/recon/rf_sniffer.py" | tee "$LOG_DIR/rf_sniffer.log";;
      "Back") return;;
    esac
  done
}

wireless_menu() {
  echo "--- Wireless Attacks ---"
  select opt in "Evil Twin (wifi_attack.py)" "BLE Crasher" "RF Signal Cloner" "Back"; do
    case $opt in
      "Evil Twin (wifi_attack.py)") python3 "$REDOT_DIR/modules/wireless/wifi_attack.py" | tee "$LOG_DIR/wifi_attack.log";;
      "BLE Crasher") python3 "$REDOT_DIR/modules/wireless/ble_crasher.py" | tee "$LOG_DIR/ble_crasher.log";;
      "RF Signal Cloner") python3 "$REDOT_DIR/modules/wireless/rf_signal_cloner.py" | tee "$LOG_DIR/rf_signal_cloner.log";;
      "Back") return;;
    esac
  done
}

hardware_menu() {
  echo "--- Hardware Interface ---"
  select opt in "UART Auto Connect" "UART Extractor" "JTAG Interface" "Back"; do
    case $opt in
      "UART Auto Connect") python3 "$REDOT_DIR/modules/hardware/uart_auto_connect.py";;
      "UART Extractor") python3 "$REDOT_DIR/modules/hardware/uart_extractor.py";;
      "JTAG Interface") python3 "$REDOT_DIR/modules/hardware/jtag_auto_interface.py";;
      "Back") return;;
    esac
  done
}

ai_attacks_menu() {
  echo "--- AI Attacks ---"
  select opt in "Image Spoof" "Model Confuser" "Voice Injection" "Back"; do
    case $opt in
      "Image Spoof") python3 "$REDOT_DIR/modules/ai_attacks/image_spoof.py";;
      "Model Confuser") python3 "$REDOT_DIR/modules/ai_attacks/model_confuser.py";;
      "Voice Injection") python3 "$REDOT_DIR/modules/ai_attacks/voice_injection.py";;
      "Back") return;;
    esac
  done
}

firmware_menu() {
  echo "--- Firmware Analysis ---"
  select opt in "Unpack & Analyze" "CVE AutoPwn" "Firmware Poisoner" "Back"; do
    case $opt in
      "Unpack & Analyze") bash "$REDOT_DIR/modules/firmware/unpack_and_analyze.sh";;
      "CVE AutoPwn") python3 "$REDOT_DIR/modules/firmware/cve_autopwn.py";;
      "Firmware Poisoner") python3 "$REDOT_DIR/modules/firmware/firmware_poisoner.py";;
      "Back") return;;
    esac
  done
}

payload_menu() {
  echo "--- Payload Deployment ---"
  select opt in "Watering Loop" "Loop Bomb" "DNS C2" "Implant Dropper" "Stealth Agent" "Back"; do
    case $opt in
      "Watering Loop") bash "$REDOT_DIR/modules/payloads/watering_loop.sh";;
      "Loop Bomb") python3 "$REDOT_DIR/modules/payloads/loop_bomb.py";;
      "DNS C2") python3 "$REDOT_DIR/modules/payloads/dns_c2.py";;
      "Implant Dropper") python3 "$REDOT_DIR/implant_dropper.py";;
      "Stealth Agent") python3 "$REDOT_DIR/modules/stealth_agent.py";;
      "Back") return;;
    esac
  done
}

iot_menu() {
  echo "--- IoT / OT Modules ---"
  select opt in "HVAC Fuzzer" "Dashboard Override" "Camera Hijack" "Access Control Replay" "Back"; do
    case $opt in
      "HVAC Fuzzer") python3 "$REDOT_DIR/modules/iot/hvac_fuzzer.py";;
      "Dashboard Override") python3 "$REDOT_DIR/modules/iot/dashboard_override.py";;
      "Camera Hijack") python3 "$REDOT_DIR/modules/iot/cam_hijack.py";;
      "Access Control Replay") python3 "$REDOT_DIR/modules/iot/access_replay.py";;
      "Back") return;;
    esac
  done
}

dashboard_menu() {
  echo "--- Copilot & Dashboard ---"
  ensure_dashboard_running
  select opt in "GPT Copilot" "Recon Assistant" "WebSocket Dashboard Server" "Open Dashboard HTML" "RTSP Viewer" "Back"; do
    case $opt in
      "GPT Copilot") python3 "$REDOT_DIR/modules/gpt_live_copilot.py";;
      "Recon Assistant") python3 "$REDOT_DIR/copilot/recon_assistant.py";;
      "WebSocket Dashboard Server") python3 "$REDOT_DIR/dashboard_ws_server.py";;
      "Open Dashboard HTML")
        if [ "$HEADLESS" -eq 0 ]; then
          python3 -m webbrowser "file://$REDOT_DIR/dashboard.html"
        else
          echo "[*] Headless mode: dashboard GUI skipped."
        fi
        ;;
      "RTSP Viewer") python3 "$REDOT_DIR/modules/rtsp_viewer.py";;
      "Back") return;;
    esac
  done
}

reporting_menu() {
  echo "--- Reporting & Intel ---"
  select opt in "Report Builder" "Intel Enricher" "Kill Chain Builder" "Copilot Chat" "Back"; do
    case $opt in
      "Report Builder") python3 "$REDOT_DIR/modules/report_builder.py";;
      "Intel Enricher") python3 "$REDOT_DIR/modules/intel_enricher.py";;
      "Kill Chain Builder") python3 "$REDOT_DIR/modules/killchain_builder.py";;
      "Copilot Chat") python3 "$REDOT_DIR/modules/copilot_chat.py";;
      "Back") return;;
    esac
  done
}

# --- MAIN LOOP ---
while true; do
  ensure_dashboard_running
  main_menu
  read main_choice
  case $main_choice in
    1) recon_menu;;
    2) wireless_menu;;
    3) hardware_menu;;
    4) ai_attacks_menu;;
    5) firmware_menu;;
    6) payload_menu;;
    7) iot_menu;;
    8) dashboard_menu;;
    9) reporting_menu;;
    10) exit 0;;
    *) echo "Invalid option. Try again.";;
  esac
done
