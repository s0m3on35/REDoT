# rtsp_viewer.py
import cv2

rtsp_url = input("Enter RTSP URL (e.g. rtsp://camera_ip/stream): ")
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("❌ Failed to open stream.")
    exit()

print("📹 Streaming... Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Stream ended or not readable.")
        break
    cv2.imshow("RTSP Viewer", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
