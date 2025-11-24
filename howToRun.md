MediaPipe Pose Tracking

Tento dokument popisuje, jak spustit **MediaPipe** model pro analýzu pohybu ve videu. Počítá se s tím, že používáte soubor `mp.py` umístěný v hlavním adresáři projektu.

---

##  1. Instalace závislostí

Model jsem testoval na **Python 3.10** (oficiální podopra je pro verzi Python: version 3.9 - 3.12).

### Instalace potřebných knihoven:

```bash
pip install opencv-python mediapipe
```

---

## 2. Příprava videa

V projektu je nyní přiloženo **ukázkové video**: [sprint.mp4](assets/sprint.mp4)

Pokud chcete použít vlastní video, vložte jej do libovolné složky a upravte cestu ve skriptu `mp.py`:

```python
video_path = "sprint.mp4"
```

---

##  3. Spuštění analýzy s MediaPipe

Spusťte hlavní skript:

```bash
python mp.py
```

Po spuštění:

* **SPACE** → pauza / pokračování
* **Q** → ukončení přehrávání

---

## 4. Tipy pro vlastní použití

* Výměna vstupního videa → změňte `video_path`
* Změna rozlišení výstupu → upravte:

```python
target_width = 1280
target_height = 720
```

* Pro vykreslení celé postavy (včetně hlavy) odstraňte filtr `head_landmarks`

---

##  Návrat do hlavního README

Vraťte se zpět na hlavní dokument projektu:

[← Zpět na hlavní stránku projektu](https://github.com/FilipStyno/SportVision)


