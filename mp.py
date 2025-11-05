import cv2
import mediapipe as mp

# Inicializace MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,        # nejpřesnější model
    enable_segmentation=False,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)

video_path = "sprint.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise RuntimeError(f"Nelze otevřít video soubor: {video_path}")

print("Analýza videa spuštěna. Stiskni 'q' pro ukončení, SPACE pro pauzu.")

target_width = 1280
target_height = 720

# Pauza
paused = False

# Landmarky hlavy/krku (které nechceme kreslit)
head_landmarks = set([0,1,2,3,4,5,6,7,8,9,10])

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            print("Konec videa.")
            break

        frame = cv2.resize(frame, (target_width, target_height))
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            # Kreslení pouze mimo hlavu
            for connection in mp_pose.POSE_CONNECTIONS:
                if connection[0] in head_landmarks or connection[1] in head_landmarks:
                    continue
                start = results.pose_landmarks.landmark[connection[0]]
                end = results.pose_landmarks.landmark[connection[1]]
                h, w, _ = frame.shape
                x0, y0 = int(start.x * w), int(start.y * h)
                x1, y1 = int(end.x * w), int(end.y * h)
                cv2.line(frame, (x0, y0), (x1, y1), (0, 255, 0), 4)

            for i, landmark in enumerate(results.pose_landmarks.landmark):
                if i in head_landmarks:
                    continue
                h, w, _ = frame.shape
                x, y = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

        cv2.imshow("Pose Tracking HD (SPACE=pauza) - sprint.mp4", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == 32:  # SPACE
        paused = not paused  # přepnutí pauzy

pose.close()
cap.release()
cv2.destroyAllWindows()
print("Analýza dokončena.")
