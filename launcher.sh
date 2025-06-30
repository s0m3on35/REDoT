#!/bin/bash
# REDOT Launcher - Fully Integrated Interactive Launcher

REDOT_PATH="$(dirname "$0")"
LOG_DIR="$REDOT_PATH/logs"
mkdir -p "$LOG_DIR"

show_menu() {
    echo "=== REDOT Toolkit Launcher ==="
    echo "Select a module to run:"
    echo "1) Recon: WiFi Scan"
    echo "2) Recon: BLE Scan"
    echo "3) Recon: RF Sniffer"
    echo "4) Attack: Evil Twin Injector"
    echo "5) Payload: Implant Dropper"
    echo "6) Payload: Stealth Agent"
    echo "7) Dashboard: WebSocket Server"
    echo "8) Dashboard: Live Web Interface"
    echo "9) Intel: Enrichment Engine"
    echo "10) AI Copilot: GPT Interface"
    echo "11) Reporting: Kill Chain Builder"
    echo "12) Reporting: Report Generator"
    echo "13) Visuals: RTSP Feed Viewer"
    echo "14) Exit"
    echo -n "Enter choice [1-14]: "
}

while true; do
    show_menu
    read choice
    case $choice in
        1)
            echo "Launching WiFi Scan..."
            python3 "$REDOT_PATH/modules/recon/wifi_scan.py" >> "$LOG_DIR/wifi_scan.log" 2>&1 &
            ;;
        2)
            echo "Launching BLE Scan..."
            python3 "$REDOT_PATH/modules/recon/ble_scan.py" >> "$LOG_DIR/ble_scan.log" 2>&1 &
            ;;
        3)
            echo "Launching RF Sniffer..."
            python3 "$REDOT_PATH/modules/recon/rf_sniffer.py" >> "$LOG_DIR/rf_sniffer.log" 2>&1 &
            ;;
        4)
            echo "Launching Evil Twin Attack..."
            python3 "$REDOT_PATH/wifi_attack.py" >> "$LOG_DIR/wifi_attack.log" 2>&1 &
            ;;
        5)
            echo "Launching Implant Dropper..."
            python3 "$REDOT_PATH/implant_dropper.py" >> "$LOG_DIR/implant_dropper.log" 2>&1 &
            ;;
        6)
            echo "Launching Stealth Agent..."
            python3 "$REDOT_PATH/modules/stealth_agent.py" >> "$LOG_DIR/stealth_agent.log" 2>&1 &
            ;;
        7)
            echo "Launching Dashboard WebSocket Server..."
            python3 "$REDOT_PATH/dashboard_ws_server.py" >> "$LOG_DIR/ws_server.log" 2>&1 &
            ;;
        8)
            echo "Opening Live Dashboard UI..."
            python3 -m webbrowser "file://$REDOT_PATH/dashboard.html" &
            ;;
        9)
            echo "Launching Intel Enricher..."
            python3 "$REDOT_PATH/modules/intel_enricher.py" >> "$LOG_DIR/intel_enricher.log" 2>&1 &
            ;;
        10)
            echo "Launching GPT Copilot..."
            python3 "$REDOT_PATH/modules/gpt_live_copilot.py" >> "$LOG_DIR/gpt_copilot.log" 2>&1 &
            ;;
        11)
            echo "Launching Kill Chain Builder..."
            python3 "$REDOT_PATH/modules/killchain_builder.py" >> "$LOG_DIR/killchain.log" 2>&1 &
            ;;
        12)
            echo "Launching Report Builder..."
            python3 "$REDOT_PATH/modules/report_builder.py" >> "$LOG_DIR/report.log" 2>&1 &
            ;;
        13)
            echo "Launching RTSP Viewer..."
            python3 "$REDOT_PATH/modules/rtsp_viewer.py" >> "$LOG_DIR/rtsp_viewer.log" 2>&1 &
            ;;
        14)
            echo "Exiting launcher."
            exit 0
            ;;
        *)
            echo "Invalid option. Please select a valid number."
            ;;
    esac
done
