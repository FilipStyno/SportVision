import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# ==========================================
# 1. VÝCHOZÍ HODNOTY
# ==========================================
DEFAULT_START_X = "1820"
DEFAULT_FINISH_X = "180"
DEFAULT_DISTANCE = "10.0"


# ==========================================
# 2. FUNKCE PRO ANALÝZU (Původní vzhled + parametry)
# ==========================================
def run_analysis(video_path, start_line_x, finish_line_x, real_distance):
    # Příprava MediaPipe
    mp_pose = mp.solutions.pose
    # Části těla k ignorování
    ignored_body_parts = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, 20, 21, 22}

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Chyba", f"Nepodařilo se otevřít video:\n{video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video načteno: {width}x{height} px")

    # Proměnné stavu
    is_running = False
    finished = False
    paused = False
    start_time = 0
    final_time = 0
    speed_kmh = 0

    # Spuštění detekce
    with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
    ) as pose:

        print("Analýza běží... MEZERNÍK = Pauza, 'q' = Ukončení.")

        while cap.isOpened():
            # Klávesnice
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == 32:  # Mezerník
                paused = not paused
                if paused:
                    print("--- PAUZA ---")
                else:
                    print("--- POKRAČUJI ---")

            if paused:
                continue

            success, frame = cap.read()
            if not success:
                print("Konec videa.")
                break

            # MediaPipe zpracování
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_bgr = frame  # Kreslíme do původního snímku

            video_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            runner_x = 0

            # Pokud je detekována postava
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Detekce hrudníku (průměr ramen)
                shoulder_left = landmarks[11]
                shoulder_right = landmarks[12]
                runner_x = int(((shoulder_left.x + shoulder_right.x) / 2) * width)
                runner_y = int(((shoulder_left.y + shoulder_right.y) / 2) * height)

                # --- LOGIKA MĚŘENÍ ---
                if not finished:
                    # START
                    if not is_running:
                        # Běh zprava (vyšší X) doleva (nižší X)
                        if runner_x <= start_line_x and runner_x > finish_line_x:
                            is_running = True
                            start_time = video_time
                            print(f"--> START v čase {video_time:.2f} s")

                    # CÍL
                    elif is_running and runner_x <= finish_line_x:
                        is_running = False
                        finished = True
                        end_time = video_time
                        final_time = end_time - start_time

                        if final_time > 0:
                            speed_ms = real_distance / final_time
                            speed_kmh = speed_ms * 3.6
                        print(f"--> CÍL! Čas: {final_time:.2f} s, {speed_kmh:.1f} km/h")

                # Vykreslení kostry
                for connection in mp_pose.POSE_CONNECTIONS:
                    start_idx, end_idx = connection
                    if start_idx in ignored_body_parts or end_idx in ignored_body_parts:
                        continue
                    p1, p2 = landmarks[start_idx], landmarks[end_idx]
                    cv2.line(image_bgr, (int(p1.x * width), int(p1.y * height)),
                             (int(p2.x * width), int(p2.y * height)), (0, 255, 0), 4)  # Tloušťka 4 jako původně

                # Tečka na hrudníku
                cv2.circle(image_bgr, (runner_x, runner_y), 10, (255, 0, 255), -1)

            # --- KRESLENÍ GRAFIKY (PŮVODNÍ VZHLED) ---
            # Start čára
            cv2.line(image_bgr, (start_line_x, 0), (start_line_x, height), (0, 255, 0), 3)
            cv2.putText(image_bgr, "START", (start_line_x - 150, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

            # Cíl čára
            cv2.line(image_bgr, (finish_line_x, 0), (finish_line_x, height), (0, 0, 255), 3)
            cv2.putText(image_bgr, "FINISH", (finish_line_x + 20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            # Info box (PŮVODNÍ VELKÝ DOLE)
            box_center_x = width // 2
            cv2.rectangle(image_bgr, (box_center_x - 200, height - 200), (box_center_x + 260, height - 30), (0, 0, 0),
                          -1)

            text_pos_time = (box_center_x - 180, height - 120)
            text_pos_speed = (box_center_x - 180, height - 60)

            if is_running:
                elapsed = video_time - start_time
                cv2.putText(image_bgr, f"Time: {elapsed:.2f} s", text_pos_time, cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (255, 255, 255), 4)
            elif finished:
                cv2.putText(image_bgr, f"FINAL: {final_time:.2f} s", text_pos_time, cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (0, 255, 0), 4)
                cv2.putText(image_bgr, f"{speed_kmh:.1f} km/h", text_pos_speed, cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                            (0, 255, 255), 3)
            else:
                cv2.putText(image_bgr, "Ready...", text_pos_time, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (200, 200, 200), 3)

            # Zmenšení pro zobrazení
            display_frame = cv2.resize(image_bgr, (1280, 720))
            cv2.imshow("SportVision - Analyza", display_frame)

    cap.release()
    cv2.destroyAllWindows()


# ==========================================
# 3. GUI (NOVÉ VYLEPŠENÉ)
# ==========================================
def open_gui():
    root = tk.Tk()
    root.title("SportVision v1.0")
    root.geometry("400x350")

    # Styl
    try:
        style = ttk.Style()
        style.theme_use('clam')
    except:
        pass

    video_path_var = tk.StringVar(value="")

    def select_file():
        path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi *.mov")])
        if path:
            video_path_var.set(path)

    def on_start():
        v_path = video_path_var.get()
        try:
            s_x = int(entry_start.get())
            f_x = int(entry_finish.get())
            dist = float(entry_dist.get())
        except ValueError:
            messagebox.showerror("Chyba", "Souřadnice a vzdálenost musí být čísla!")
            return

        if not v_path:
            messagebox.showwarning("Pozor", "Nebylo vybráno žádné video.")
            return

        root.destroy()
        run_analysis(v_path, s_x, f_x, dist)

    # --- Rozložení ---
    lbl_title = ttk.Label(root, text="Konfigurace analýzy", font=("Helvetica", 16, "bold"))
    lbl_title.pack(pady=15)

    frame_file = ttk.LabelFrame(root, text="Vstupní video")
    frame_file.pack(fill="x", padx=20, pady=5)

    btn_browse = ttk.Button(frame_file, text="Vybrat soubor...", command=select_file)
    btn_browse.pack(side="left", padx=10, pady=10)

    lbl_path = ttk.Label(frame_file, textvariable=video_path_var, foreground="blue")
    lbl_path.pack(side="left", padx=5)

    frame_calib = ttk.LabelFrame(root, text="Kalibrace dráhy")
    frame_calib.pack(fill="x", padx=20, pady=10)

    ttk.Label(frame_calib, text="Start (X px):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_start = ttk.Entry(frame_calib, width=10)
    entry_start.insert(0, DEFAULT_START_X)
    entry_start.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_calib, text="Cíl (X px):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_finish = ttk.Entry(frame_calib, width=10)
    entry_finish.insert(0, DEFAULT_FINISH_X)
    entry_finish.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame_calib, text="Vzdálenost (m):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_dist = ttk.Entry(frame_calib, width=10)
    entry_dist.insert(0, DEFAULT_DISTANCE)
    entry_dist.grid(row=2, column=1, padx=5, pady=5)

    btn_start = tk.Button(root, text="SPUSTIT ANALÝZU", command=on_start,
                          bg="#28a745", fg="white", font=("Arial", 12, "bold"), height=2)
    btn_start.pack(fill="x", padx=40, pady=20)

    root.mainloop()


if __name__ == "__main__":
    open_gui()