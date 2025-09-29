import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 pose model
model = YOLO("yolo11m-pose.pt")

# Open video
cap = cv2.VideoCapture("sprint.mp4")
paused = False

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

# Keep track of current frame
current_frame_number = 0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break
        current_frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    else:
        # When paused, jump to current frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_number)
        ret, frame = cap.read()
        if not ret:
            break

    results = model(frame)
    annotated_frame = results[0].plot()

    # Knee angles overlay
    for r in results:
        keypoints = r.keypoints.xy.cpu().numpy()
        if len(keypoints) > 0:
            person = keypoints[0]
            left_hip, left_knee, left_ankle = person[11], person[13], person[15]
            right_hip, right_knee, right_ankle = person[12], person[14], person[16]

            left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

            cv2.putText(annotated_frame, f"L Knee: {left_knee_angle:.1f}", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"R Knee: {right_knee_angle:.1f}", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Pose with Angles", annotated_frame)

    key = cv2.waitKey(0 if paused else 30) & 0xFF  # wait indefinitely if paused
    if key == ord("q"):
        break
    elif key == ord(" "):
        paused = not paused
    elif key == 81:  # left arrow
        paused = True
        current_frame_number = max(0, current_frame_number - 1)
    elif key == 83:  # right arrow
        paused = True
        current_frame_number = min(total_frames - 1, current_frame_number + 1)

cap.release()
cv2.destroyAllWindows()
