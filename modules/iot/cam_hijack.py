# cam_hijack.py - Attack RTSP & ONVIF streams
print("📷 Camera Hijack Module")

# Simulated RTSP brute-force and ONVIF control
targets = ['192.168.1.100', '192.168.1.101']
for ip in targets:
    print(f"[+] Attempting RTSP login on {ip}...")
    print(f"    -> RTSP stream accessed: rtsp://{ip}/live (simulated)")
    print(f"    -> ONVIF control enabled: Panning camera at {ip} (simulated)")
