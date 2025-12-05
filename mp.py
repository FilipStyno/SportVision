import cv2
import mediapipe as mp

# --- KONFIGURACE ---
VIDEO_PATH = "walk.mp4"
REAL_DISTANCE_METERS = 10.0

# !! ZDE DOPLŇ HODNOTY Z KALIBRACE (pro 1920x1080) !!
START_LINE_X = 1820  # Příklad (u čísla 30)
FINISH_LINE_X = 180  # Příklad (u čísla 20)

# Korekce perspektivy (v pixelech)
# Pokud běžíš "před zdí", možná budeš muset čáry posunout.
# Kladné číslo posouvá doprava, záporné doleva.
PERSPECTIVE_SHIFT = 0

# --- INICIALIZACE ---
mp_pose = mp.solutions.pose
excluded_landmarks = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, 20, 21, 22}


def main():
    cap = cv2.VideoCapture(VIDEO_PATH)

    # Zjistíme reálné rozměry videa (očekáváme 1920x1080)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Rozlišení videa: {width}x{height}")

    # Aplikace posunu čar
    calibrated_start = START_LINE_X + PERSPECTIVE_SHIFT
    calibrated_finish = FINISH_LINE_X + PERSPECTIVE_SHIFT

    is_running = False
    finished = False
    start_time_video = 0
    final_time = 0
    average_speed_kmh = 0

    with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # Pro 1080p určitě nech 1, dvojka by byla pomalá
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
    ) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            # Zpracování v plném rozlišení (žádný resize!)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            current_video_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            runner_x_px = 0

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Výpočet středu boků
                hip_left = landmarks[23]
                hip_right = landmarks[24]

                # Pozor: MediaPipe vrací souřadnice 0.0 až 1.0
                # Musíme je vynásobit skutečnou šířkou videa (1920)
                runner_x_px = int(((hip_left.x + hip_right.x) / 2) * width)
                runner_y_px = int(((hip_left.y + hip_right.y) / 2) * height)

                # --- LOGIKA (ZPRAVA DOLEVA) ---
                if not finished:
                    # Čekání na start (běžec je vpravo, X > Start)
                    if not is_running:
                        if runner_x_px <= calibrated_start and runner_x_px > calibrated_finish:
                            is_running = True
                            start_time_video = current_video_time
                            print(f"START v čase {current_video_time:.2f}s")

                    # Běh a cíl (běžec je vlevo, X < Cíl)
                    elif is_running and runner_x_px <= calibrated_finish:
                        is_running = False
                        finished = True
                        end_time_video = current_video_time

                        final_time = end_time_video - start_time_video
                        speed_ms = REAL_DISTANCE_METERS / final_time if final_time > 0 else 0
                        average_speed_kmh = speed_ms * 3.6
                        print(f"CÍL! Čas: {final_time:.2f}s, Rychlost: {average_speed_kmh:.2f} km/h")

                # Vykreslení
                for connection in mp_pose.POSE_CONNECTIONS:
                    s, e = connection
                    if s in excluded_landmarks or e in excluded_landmarks: continue
                    p1, p2 = landmarks[s], landmarks[e]
                    # Kreslíme do velkého obrazu
                    cv2.line(image, (int(p1.x * width), int(p1.y * height)),
                             (int(p2.x * width), int(p2.y * height)), (0, 255, 0), 4, cv2.LINE_AA)

                cv2.circle(image, (runner_x_px, runner_y_px), 15, (255, 0, 255), -1)

            # --- GRAFIKA ---
            # Čáry kreslíme přes celou výšku 1080px
            cv2.line(image, (calibrated_start, 0), (calibrated_start, height), (0, 255, 0), 3)
            cv2.putText(image, "START (30m)", (calibrated_start - 200, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0),
                        3)

            cv2.line(image, (calibrated_finish, 0), (calibrated_finish, height), (0, 0, 255), 3)
            cv2.putText(image, "CIL (20m)", (calibrated_finish - 150, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255),
                        3)

            # INFO BOX
            cv2.rectangle(image, (width // 2 - 200, height - 200), (width // 2 + 200, height - 50), (0, 0, 0), -1)
            text_x = width // 2 - 180

            if is_running:
                elapsed = current_video_time - start_time_video
                cv2.putText(image, f"Cas: {elapsed:.2f} s", (text_x, height - 120), cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (255, 255, 255), 4)
            elif finished:
                cv2.putText(image, f"FINAL: {final_time:.2f} s", (text_x, height - 120), cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (0, 255, 0), 4)
                cv2.putText(image, f"{average_speed_kmh:.1f} km/h", (text_x, height - 60), cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, (0, 255, 255), 3)
            else:
                cv2.putText(image, "Pripraven...", (text_x, height - 120), cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                            (200, 200, 200), 3)

            # FINÁLNÍ ZOBRAZENÍ - Zmenšíme jen pro oko, výpočty zůstaly v HD
            display_frame = cv2.resize(image, (1280, 720))
            cv2.imshow("Sprint Analysis HD", display_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()