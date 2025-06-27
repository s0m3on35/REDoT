# Loop Bomb Payload
print("💣 Activating Loop Bomb...")
# Simulated loop of movement or watering commands
for i in range(5):
    print(f"Loop {i+1}: Sending command -> MOVE_FORWARD")
    print(f"Loop {i+1}: Sending command -> STOP")
    print(f"Loop {i+1}: Sending command -> WATER_ON")
    print(f"Loop {i+1}: Sending command -> WATER_OFF")
print("Loop sequence complete (simulated).")
