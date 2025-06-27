# access_replay.py - Replay RFID/UHF/PINs
print(" Access Replay Module")

# Simulated RFID cloning and PIN brute force
rfid_uid = "04:A3:BC:12:9F:88"
print(f"[+] Cloned RFID tag UID: {rfid_uid}")

print("    -> Sending cloned signal to door controller... (simulated)")

# Simulate PIN guessing loop
for pin in ['1234', '0000', '9999']:
    print(f"    -> Trying PIN {pin}... [FAIL]")
print("    -> Max attempts reached, lockout triggered (simulated).")
