# AI Camera Spoofing Module
import cv2
print("📸 Launching camera spoofing module...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot access camera.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.putText(frame, "👁️ Adversarial Spoof Active", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        cv2.imshow("RedOT Cam Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
