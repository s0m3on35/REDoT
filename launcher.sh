#!/bin/bash
# REDOT Launcher 

REDOT_PATH="$(dirname "$0")"
LOG_DIR="$REDOT_PATH/logs"
REQ_FILE="$REDOT_PATH/requirements.txt"
PYTHON=$(which python3)

mkdir -p "$LOG_DIR"

# --- System Dependencies Check ---
check_bin() {
    local bin="$1"
    if ! command -v "$bin" &> /dev/null; then
        echo "[!] Missing system dependency: $bin"
        MISSING_BINS+=("$bin")
    fi
}

echo "[*] Checking system dependencies..."
MISSING_BINS=()
for bin in aircrack-ng hostapd iw ifconfig curl git; do
    check_bin "$bin"
done

if [ ${#MISSING_BINS[@]} -gt 0 ]; then
    echo "[!] The following system tools are missing:"
    for b in "${MISSING_BINS[@]}"; do echo "   - $b"; done

    echo "[*] Attempting to auto-install using apt (Debian/Ubuntu)..."
    if [ "$(id -u)" -ne 0 ]; then
        echo "[!] Please run as root or install manually: ${MISSING_BINS[*]}"
        exit 1
    fi

    apt update && apt install -y "${MISSING_BINS[@]}"
    if [ $? -ne 0 ]; then
        echo "[!] Auto-install failed. Install manually and re-run."
        exit 1
    fi
fi

# --- Python Dependencies Check ---
echo "[*] Checking Python dependencies..."
if [ ! -f "$REQ_FILE" ]; then
  echo "[!] requirements.txt not found. Creating default list..."
  cat <<EOF > "$REQ_FILE"
scapy
rich
requests
flask
websocket-server
pyyaml
aioblescan
blesuite
numpy
opencv-python
pillow
matplotlib
torch
transformers
tflite-runtime
EOF
fi

$PYTHON -m pip install --quiet --upgrade pip
$PYTHON -m pip install --quiet -r "$REQ_FILE"

# --- Interactive Menu ---
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
            $PYTHON "$REDOT_PATH/modules/recon/wifi_scan.py" >> "$LOG_DIR/wifi_scan.log" 2>&1 &
            ;;
        2)
            echo "Launching BLE Scan..."
            $PYTHON "$REDOT_PATH/modules/recon/ble_scan.py" >> "$LOG_DIR/ble_scan.log" 2>&1 &
            ;;
        3)
            echo "Launching RF Sniffer..."
            $PYTHON "$REDOT_PATH/modules/recon/rf_sniffer.py" >> "$LOG_DIR/rf_sniffer.log" 2>&1 &
            ;;
        4)
            echo "Launching Evil Twin Attack..."
            $PYTHON "$REDOT_PATH/wifi_attack.py" >> "$LOG_DIR/wifi_attack.log" 2>&1 &
            ;;
        5)
            echo "Launching Implant Dropper..."
            $PYTHON "$REDOT_PATH/implant_dropper.py" >> "$LOG_DIR/implant_dropper.log" 2>&1 &
            ;;
        6)
            echo "Launching Stealth Agent..."
            $PYTHON "$REDOT_PATH/modules/stealth_agent.py" >> "$LOG_DIR/stealth_agent.log" 2>&1 &
            ;;
        7)
            echo "Launching Dashboard WebSocket Server..."
            $PYTHON "$REDOT_PATH/dashboard_ws_server.py" >> "$LOG_DIR/ws_server.log" 2>&1 &
            ;;
        8)
            echo "Opening Live Dashboard UI..."
            $PYTHON -m webbrowser "file://$REDOT_PATH/dashboard.html" &
            ;;
        9)
            echo "Launching Intel Enricher..."
            $PYTHON "$REDOT_PATH/modules/intel_enricher.py" >> "$LOG_DIR/intel_enricher.log" 2>&1 &
            ;;
        10)
            echo "Launching GPT Copilot..."
            $PYTHON "$REDOT_PATH/modules/gpt_live_copilot.py" >> "$LOG_DIR/gpt_copilot.log" 2>&1 &
            ;;
        11)
            echo "Launching Kill Chain Builder..."
            $PYTHON "$REDOT_PATH/modules/killchain_builder.py" >> "$LOG_DIR/killchain.log" 2>&1 &
            ;;
        12)
            echo "Launching Report Builder..."
            $PYTHON "$REDOT_PATH/modules/report_builder.py" >> "$LOG_DIR/report.log" 2>&1 &
            ;;
        13)
            echo "Launching RTSP Viewer..."
            $PYTHON "$REDOT_PATH/modules/rtsp_viewer.py" >> "$LOG_DIR/rtsp_viewer.log" 2>&1 &
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
