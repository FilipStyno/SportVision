# Jak spustit a nastavit SportVision

Tento dokument slouží jako manuál pro spuštění a **hlavně konfiguraci** skriptu pro analýzu sprintu.

Program je navržen tak, aby byl flexibilní. Většinu nastavení (kde je start, cíl, kvalita modelu) můžete upravit změnou proměnných přímo na začátku souboru `mp.py`.

---

## 1. Prvotní instalace
Pokud spouštíte projekt poprvé, nainstalujte potřebné knihovny.
Doporučená verze Pythonu: **3.10** (podporováno 3.9–3.12).

```bash
pip install opencv-python mediapipe

```

---

## 2. Rychlé spuštění (Ukázka)

Pro otestování funkčnosti s přiloženým videem stačí spustit hlavní skript.
*Ujistěte se, že v `mp.py` je nastavena cesta:* `VIDEO_PATH = "assets/run2.mp4"`

```bash
python mp.py

```

**Ovládání:**

* **SPACE** → Pauza / Pokračování
* **Q** → Ukončení

---

## 3. ⚙️ Konfigurace a kalibrace

Protože každé video je natočeno z jiného úhlu a vzdálenosti, je nutné skript nastavit. Všechna nastavení najdete **na začátku souboru `mp.py**` v sekci `KONFIGURACE`.

### A. Výměna videa

Chcete-li analyzovat vlastní běh, změňte cestu k souboru:

```python
VIDEO_PATH = "moje_video.mp4"  # Cesta k vašemu souboru

```

### B. Nastavení Startu a Cíle (Manuální kalibrace)

Program potřebuje vědět, na kterém pixelu (souřadnice X) se nachází startovní a cílová čára.

**Jak zjistit souřadnice X?**

1. Otevřete video v grafickém editoru nebo přehrávači, který ukazuje souřadnice myši.
2. Najeďte myší na místo startu a opište si číslo **X**.
3. To samé udělejte pro cíl.

Upravte tyto řádky v kódu:

```python
# Příklad: Start je vpravo (pixel 1650), Cíl je vlevo (pixel 450)
START_LINE_X = 1650   
FINISH_LINE_X = 450
REAL_DISTANCE_METERS = 10.0  # Skutečná vzdálenost mezi body v metrech

```

### C. Rychlost vs. Přesnost

MediaPipe nabízí tři úrovně složitosti modelu (`model_complexity`):

* **0** = Nejrychlejší (pro slabší PC, méně přesné).
* **1** = Zlatý střed (doporučeno).
* **2** = Nejpřesnější (náročné, může video zpomalit).

### E. Změna směru běhu

Skript je primárně nastaven pro běh **Zprava (větší X) do Leva (menší X)**.

Pokud běžíte opačně (**Zleva doprava**), nahraďte v kódu celou sekci logiky tímto blokem:

```python
# --- LOGIKA MĚŘENÍ (BĚH ZLEVA -> DOPRAVA) ---
if not finished:
    # START
    if not is_running:
        if runner_x >= START_LINE_X and runner_x < FINISH_LINE_X:
            is_running = True
            start_time = video_time
            print(f"--> START v čase {video_time:.2f} s")

    # CÍL
    elif is_running and runner_x >= FINISH_LINE_X:
        is_running = False
        finished = True
        end_time = video_time

        final_time = end_time - start_time
        if final_time > 0:
            speed_ms = REAL_DISTANCE_METERS / final_time
            speed_kmh = speed_ms * 3.6
        print(f"--> CÍL! Čas: {final_time:.2f} s, Rychlost: {speed_kmh:.1f} km/h")

```


---

## 4. Řešení problémů

**Video se seká (nízké FPS)**

* Snižte `model_complexity` na 0.
* Snižte rozlišení videa

**Měření nezačne**

* Zkontrolujte `START_LINE_X`. Běžec musí začínat "před" čárou a protnout ji.

[← Zpět na hlavní stránku projektu](https://github.com/FilipStyno/SportVision)
