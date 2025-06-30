#!/bin/bash
# REDOT Launcher - Interactive module launcher with logging

REDOT_PATH="$(dirname "$0")"
LOG_DIR="$REDOT_PATH/logs"
mkdir -p "$LOG_DIR"

show_menu() {
    echo "=== REDOT Toolkit Launcher ==="
    echo "Select a module to run:"
    echo "1) Recon: WiFi Scan"
    echo "2) Remote Agent Uploader"
    echo "3) Intel Leak Tracker"
    echo "4) Forensic Detonator (Anti-Analysis Trap)"
    echo "5) Exit"
    echo -n "Enter choice [1-5]: "
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
            echo "Launching Remote Agent Uploader..."
            python3 "$REDOT_PATH/remote_agent_uploader.py" >> "$LOG_DIR/agent_uploader.log" 2>&1 &
            ;;
        3)
            echo "Launching Intel Leak Tracker..."
            python3 "$REDOT_PATH/intel_leak_tracker.py" >> "$LOG_DIR/leak_tracker.log" 2>&1 &
            ;;
        4)
            echo "Launching Forensic Detonator..."
            python3 "$REDOT_PATH/forensic_detonator.py" >> "$LOG_DIR/forensic_detonator.log" 2>&1 &
            ;;
        5)
            echo "Exiting launcher."
            exit 0
            ;;
        *)
            echo "Invalid option. Please select 1-5."
            ;;
    esac
done
