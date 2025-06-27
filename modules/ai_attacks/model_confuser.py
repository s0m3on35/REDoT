# AI Model Confuser
import cv2
import numpy as np

print("Model Confuser: Starting adversarial spoof...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera access failed.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply fake "adversarial" effect (placeholder)
    noise = np.random.normal(0, 50, frame.shape).astype(np.uint8)
    adversarial_frame = cv2.add(frame, noise)

    cv2.putText(adversarial_frame, "Adversarial Pattern Active", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("RedOT AI Vision Attack", adversarial_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
