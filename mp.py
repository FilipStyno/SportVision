import cv2
import mediapipe as mp

# ==========================================
# 1. ZÁKLADNÍ NASTAVENÍ
# ==========================================

# Název tvého videa
VIDEO_PATH = "run2.mp4"

# Jak dlouhá je trať ve skutečnosti?
REAL_DISTANCE_METERS = 10.0

# Kde je START a CÍL v obraze?
# (Otevři si video v Malování/Editoru, najeď myší na čáru a opiš souřadnici X)
# Příklad: Běžíš zprava doleva
START_LINE_X = 1820
FINISH_LINE_X = 180

# ==========================================
# KONEC NASTAVENÍ
# ==========================================

# Příprava nástroje pro detekci postavy (MediaPipe)
mp_pose = mp.solutions.pose

# Seznam částí těla, které ignorujeme (obličej a prsty), aby byl obraz čistší
ignored_body_parts = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, 20, 21, 22}


def main():
    # Načtení videa
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Chyba: Nemůžu najít video '{VIDEO_PATH}'. Zkontroluj název.")
        return

    # Zjištění velikosti videa
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video načteno: {width}x{height} pixelů")

    # Proměnné pro měření času
    is_running = False  # Běží zrovna časomíra?
    finished = False  # Doběhl už do cíle?

    # --- PROMĚNNÁ PRO PAUZU ---
    paused = False

    start_time = 0
    final_time = 0
    speed_kmh = 0

    # Spuštění "mozku" pro detekci pohybu
    with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
    ) as pose:

        print("Analýza běží... MEZERNÍK = Pauza, 'q' = Ukončení.")

        while cap.isOpened():
            # --- OVLÁDÁNÍ KLÁVESNICE ---
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == 32: # Space
                paused = not paused
                if paused:
                    print("--- PAUZA ---")
                else:
                    print("--- POKRAČUJI ---")

            if paused:
                continue

            # ---------------------------------------------------

            success, frame = cap.read()
            if not success:
                print("Konec videa.")
                break

            # 1. Získání dat z videa
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)

            # Zpět na barvy pro lidské oko
            image_bgr = frame

            video_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            runner_x = 0

            # Pokud vidíme postavu...
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # ---  Měříme podle hrudníku (střed ramen) ---
                # Landmark 11 = Levé rameno, Landmark 12 = Pravé rameno
                shoulder_left = landmarks[11]
                shoulder_right = landmarks[12]

                # Průměr X a Y souřadnic ramen = střed horní části hrudníku
                runner_x = int(((shoulder_left.x + shoulder_right.x) / 2) * width)
                runner_y = int(((shoulder_left.y + shoulder_right.y) / 2) * height)

                # --- LOGIKA MĚŘENÍ (BĚH ZPRAVA -> DOLEVA) ---
                if not finished:
                    # START
                    if not is_running:
                        if runner_x <= START_LINE_X and runner_x > FINISH_LINE_X:
                            is_running = True
                            start_time = video_time
                            print(f"--> START v čase {video_time:.2f} s")

                    # CÍL
                    elif is_running and runner_x <= FINISH_LINE_X:
                        is_running = False
                        finished = True
                        end_time = video_time

                        final_time = end_time - start_time
                        if final_time > 0:
                            speed_ms = REAL_DISTANCE_METERS / final_time
                            speed_kmh = speed_ms * 3.6
                        print(f"--> CÍL! Čas: {final_time:.2f} s, Rychlost: {speed_kmh:.1f} km/h")

                # --- KRESLENÍ KOSTRY ---
                for connection in mp_pose.POSE_CONNECTIONS:
                    start_idx, end_idx = connection
                    if start_idx in ignored_body_parts or end_idx in ignored_body_parts:
                        continue

                    p1 = landmarks[start_idx]
                    p2 = landmarks[end_idx]

                    x1, y1 = int(p1.x * width), int(p1.y * height)
                    x2, y2 = int(p2.x * width), int(p2.y * height)

                    cv2.line(image_bgr, (x1, y1), (x2, y2), (0, 255, 0), 4, cv2.LINE_AA)

                # Tečka na hrudníku (naše měřící čidlo)
                cv2.circle(image_bgr, (runner_x, runner_y), 10, (255, 0, 255), -1)

            # --- KRESLENÍ GRAFIKY ---
            # Start
            cv2.line(image_bgr, (START_LINE_X, 0), (START_LINE_X, height), (0, 255, 0), 3)
            cv2.putText(image_bgr, "START", (START_LINE_X - 120, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

            # Cíl
            cv2.line(image_bgr, (FINISH_LINE_X, 0), (FINISH_LINE_X, height), (0, 0, 255), 3)
            cv2.putText(image_bgr, "CIL", (FINISH_LINE_X - 80, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            # Info box
            box_center_x = width // 2
            cv2.rectangle(image_bgr, (box_center_x - 200, height - 200), (box_center_x + 260, height - 30), (0, 0, 0), -1)

            text_pos_time = (box_center_x - 180, height - 120)
            text_pos_speed = (box_center_x - 180, height - 60)

            if is_running:
                elapsed = video_time - start_time
                cv2.putText(image_bgr, f"Cas: {elapsed:.2f} s", text_pos_time, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
            elif finished:
                cv2.putText(image_bgr, f"FINAL: {final_time:.2f} s", text_pos_time, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
                cv2.putText(image_bgr, f"{speed_kmh:.1f} km/h", text_pos_speed, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            else:
                cv2.putText(image_bgr, "Pripraven...", text_pos_time, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (200, 200, 200), 3)

            # Zobrazení
            display_frame = cv2.resize(image_bgr, (1280, 720))
            cv2.imshow("SportVision - Analyza", display_frame)

    cap.release()
    cv2.destroyAllWindows()
    print("Program ukončen.")


if __name__ == "__main__":
    main()
