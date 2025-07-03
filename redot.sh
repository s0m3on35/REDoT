#!/bin/bash
# REDOT Toolkit Launcher

REDOT_PATH="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$REDOT_PATH/logs"
REQ_FILE="$REDOT_PATH/requirements.txt"
PYTHON=$(which python3)

mkdir -p "$LOG_DIR"

# --- System Dependencies ---
echo "[*] Checking system dependencies..."
MISSING_BINS=()
for bin in aircrack-ng hostapd iw ifconfig curl git; do
    if ! command -v "$bin" &> /dev/null; then
        echo "[!] Missing: $bin"
        MISSING_BINS+=("$bin")
    fi
done

if [ ${#MISSING_BINS[@]} -gt 0 ]; then
    echo "[!] Required tools missing: ${MISSING_BINS[*]}"
    if [ "$(id -u)" -ne 0 ]; then
        echo "[!] Run as root or install manually: ${MISSING_BINS[*]}"
        exit 1
    fi
    echo "[*] Attempting to install via apt..."
    apt update && apt install -y "${MISSING_BINS[@]}"
    if [ $? -ne 0 ]; then
        echo "[!] Installation failed. Please install manually."
        exit 1
    fi
fi

# --- Python Dependencies ---
echo "[*] Ensuring Python environment..."
if [ ! -f "$REQ_FILE" ]; then
    echo "[*] Creating default requirements.txt..."
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
pyttsx3
PyQt5
EOF
fi

$PYTHON -m pip install --upgrade pip >/dev/null 2>&1
$PYTHON -m pip install -r "$REQ_FILE" >/dev/null 2>&1

# --- Optional CLI Only ---
if [[ "$1" == "--cli" ]]; then
    echo "[*] CLI mode enabled."
else
    echo "[*] Starting WebSocket server..."
    $PYTHON "$REDOT_PATH/webgui/dashboard_ws_server.py" >> "$LOG_DIR/ws_server.log" 2>&1 &
    sleep 2
    echo "[*] Opening dashboard UI..."
    $PYTHON -m webbrowser "file://$REDOT_PATH/webgui/dashboard.html" &
fi

# --- Menu ---
show_menu() {
    echo ""
    echo "=============================="
    echo " REDOT Toolkit Main Launcher"
    echo "=============================="
    echo " 1) Launch REDOT GUI (PyQt5)"
    echo " 2) Run WebSocket Server Only"
    echo " 3) Open Dashboard Interface"
    echo " 4) Run CLI Menu (offensive_chainer.py)"
    echo " 5) Run Wi-Fi Scan"
    echo " 6) Run BLE Scan"
    echo " 7) Run RF Sniffer"
    echo " 8) Run Evil Twin Attack"
    echo " 9) Drop Implant"
    echo "10) Launch Stealth Agent"
    echo "11) Exit"
    echo "------------------------------"
    echo -n "Enter selection: "
}

while true; do
    show_menu
    read choice
    case $choice in
        1) echo "[*] Launching GUI..."; $PYTHON "$REDOT_PATH/gui_launcher.py" >> "$LOG_DIR/gui.log" 2>&1 ;;
        2) echo "[*] Launching WebSocket server..."; $PYTHON "$REDOT_PATH/webgui/dashboard_ws_server.py" >> "$LOG_DIR/ws_server.log" 2>&1 ;;
        3) echo "[*] Opening dashboard..."; $PYTHON -m webbrowser "file://$REDOT_PATH/webgui/dashboard.html" ;;
        4) echo "[*] Starting CLI orchestrator..."; $PYTHON "$REDOT_PATH/modules/orchestration/offensive_chainer.py" ;;
        5) echo "[*] Starting Wi-Fi scan..."; $PYTHON "$REDOT_PATH/modules/recon/wifi_scan.py" >> "$LOG_DIR/wifi_scan.log" 2>&1 ;;
        6) echo "[*] Starting BLE scan..."; $PYTHON "$REDOT_PATH/modules/recon/ble_scan.py" >> "$LOG_DIR/ble_scan.log" 2>&1 ;;
        7) echo "[*] Starting RF sniffer..."; $PYTHON "$REDOT_PATH/modules/recon/rf_sniffer.py" >> "$LOG_DIR/rf_sniffer.log" 2>&1 ;;
        8) echo "[*] Running Evil Twin..."; $PYTHON "$REDOT_PATH/wifi_attack.py" >> "$LOG_DIR/wifi_attack.log" 2>&1 ;;
        9) echo "[*] Dropping implant..."; $PYTHON "$REDOT_PATH/implant_dropper.py" >> "$LOG_DIR/implant_dropper.log" 2>&1 ;;
        10) echo "[*] Launching stealth agent..."; $PYTHON "$REDOT_PATH/modules/stealth_agent.py" >> "$LOG_DIR/stealth_agent.log" 2>&1 ;;
        11) echo "[*] Exiting."; exit 0 ;;
        *) echo "[!] Invalid option." ;;
    esac
done
