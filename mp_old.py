import cv2
import mediapipe as mp
import time

# Inicializace MediaPipe
mp_pose = mp.solutions.pose

# Nastavení cesty a rozlišení
video_path = "sprint.mp4"
target_width = 1280
target_height = 720

# DEFINICE BODŮ K VYLOUČENÍ
# 0-10: Hlava a obličej
# 17-22: Prsty na rukou 
excluded_landmarks = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    17, 18, 19, 20, 21, 22
}


def main():
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Chyba: Nelze otevřít {video_path}")
        return

    # Context Manager
    with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # přesnost modelu: 1 = rychlost (26 FPS), 2 = větší přesnost (9 FPS)
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
    ) as pose:

        print("Analýza spuštěna. 'q' = konec, 'SPACE' = pauza.")
        paused = False
        prev_time = 0

        while cap.isOpened():
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == 32:  # SPACE
                paused = not paused

            if paused:
                continue

            ret, frame = cap.read()
            if not ret:
                print("Konec videa.")
                break

            # Resize
            frame = cv2.resize(frame, (target_width, target_height))

            # Optimalizace: Writeable = False
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = pose.process(image)

            # Zpět na BGR pro kreslení
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                h, w, _ = image.shape

                # 1. Kreslení spojnic (kostí)
                for connection in mp_pose.POSE_CONNECTIONS:
                    start_idx = connection[0]
                    end_idx = connection[1]

                    # Pokud je začátek NEBO konec spojnice na seznamu vyloučených, nekreslíme
                    if start_idx in excluded_landmarks or end_idx in excluded_landmarks:
                        continue

                    start = results.pose_landmarks.landmark[start_idx]
                    end = results.pose_landmarks.landmark[end_idx]

                    x0, y0 = int(start.x * w), int(start.y * h)
                    x1, y1 = int(end.x * w), int(end.y * h)

                    cv2.line(image, (x0, y0), (x1, y1), (0, 255, 0), 3, cv2.LINE_AA)

                # 2. Kreslení bodů (kloubů)
                for i, landmark in enumerate(results.pose_landmarks.landmark):
                    # Pokud je bod na seznamu vyloučených, nekreslíme
                    if i in excluded_landmarks:
                        continue

                    # Visibility check
                    if landmark.visibility < 0.5:
                        continue

                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(image, (cx, cy), 6, (0, 0, 255), -1, cv2.LINE_AA)
                    cv2.circle(image, (cx, cy), 6, (255, 255, 255), 1, cv2.LINE_AA)

            # FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time > 0 else 0
            prev_time = curr_time

            cv2.putText(image, f"FPS: {int(fps)}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            cv2.imshow("Sprint Analysis (No Fingers)", image)

    cap.release()
    cv2.destroyAllWindows()
    print("Analýza dokončena.")


if __name__ == "__main__":
    main()