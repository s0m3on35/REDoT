# copilot_chat.py
import readline

print(" RedOT Copilot Chat – Ask me anything (type 'exit' to quit):")
while True:
    q = input("> ")
    if q.strip().lower() == "exit":
        break
    print("> Based on your input, consider running 'firmware_poisoner.py' with custom payloads.")
    print("    You can also chain with 'dns_c2.py' for exfiltration.
")
