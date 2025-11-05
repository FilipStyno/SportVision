import cv2
from ultralytics import YOLO

# Načti YOLOv11 pose model (stáhne se automaticky, pokud ho nemáš)
model = YOLO("yolo11m-pose.pt")

# Načti video
cap = cv2.VideoCapture("sprint1mp4.mp4")
paused = False

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated_frame = results[0].plot()

        cv2.imshow("YOLOv11 Pose Estimation", annotated_frame)

    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):      # ukončení
        break
    elif key == ord(' '):    # mezerník = pauza / pokračování
        paused = not paused

cap.release()
cv2.destroyAllWindows()