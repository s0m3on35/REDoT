# Voice Injection via TTS or ultrasonic simulation
import pyttsx3
print("🔊 Voice Injection: Generating TTS command...")

engine = pyttsx3.init()
command = "Start watering. System override. Reboot now."
engine.say(command)
engine.runAndWait()

print(f"Command played: '{command}'")
