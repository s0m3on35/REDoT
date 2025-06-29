#!/usr/bin/env python3
import yaml
import json
import os
from pathlib import Path

CONFIG_PATH = Path("config/targets.yaml")

DEFAULT_CONFIG = {
    'robots': [
        {
            'name': 'Bot01',
            'ip': '192.168.0.10',
            'mac': 'AA:BB:CC:DD:EE:01',
            'location': 'Garden Area',
            'protocols': ['wifi', 'ble'],
            'tags': ['irrigation', 'perimeter'],
            'notes': 'Primary watering bot'
        },
        {
            'name': 'Sensor-Cam-A',
            'ip': '192.168.0.20',
            'mac': 'AA:BB:CC:DD:EE:02',
            'location': 'North Fence',
            'protocols': ['rtsp', 'wifi'],
            'tags': ['camera', 'motion', 'rtsp'],
            'notes': 'RTSP-enabled motion camera'
        },
        {
            'name': 'HVAC-Unit01',
            'ip': '192.168.0.30',
            'mac': 'AA:BB:CC:DD:EE:03',
            'location': 'Shed',
            'protocols': ['modbus', 'http'],
            'tags': ['hvac', 'temperature'],
            'notes': 'Exposed HVAC panel'
        },
        {
            'name': 'Controller-Z',
            'ip': '192.168.0.40',
            'mac': 'AA:BB:CC:DD:EE:04',
            'location': 'Control Room',
            'protocols': ['zigbee', 'mqtt'],
            'tags': ['core', 'gateway'],
            'notes': 'Zigbee hub controller with MQTT broker'
        }
    ],
    'defaults': {
        'timeout': 5,
        'retries': 2,
        'stealth_mode': True
    }
}

def ensure_config_exists():
    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f)

def load_targets():
    ensure_config_exists()
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def get_targets_json():
    data = load_targets()
    return json.dumps(data['robots'], indent=2)

def update_or_add_robot_entry(new_robot):
    config = load_targets()
    updated = False
    for robot in config['robots']:
        if robot['name'] == new_robot['name']:
            robot.update(new_robot)
            updated = True
            break
    if not updated:
        config['robots'].append(new_robot)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f)

# Example CLI
if __name__ == "__main__":
    ensure_config_exists()
    print("[+] Available Robots:")
    for bot in load_targets()['robots']:
        print(f" - {bot['name']} @ {bot['ip']} ({', '.join(bot['protocols'])})")
