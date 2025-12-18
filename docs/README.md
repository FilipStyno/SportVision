# SportVision — Analýza sprintu a měření rychlosti z videa

<p align="center"><em>Projekt zaměřený na automatické měření času a rychlosti běžce pomocí počítačového vidění.</em></p>

<p align="center">
  <img src="/assets/pose.png" width="600" alt="Ukázka analýzy sprintu">
</p>

##  Cíl projektu
Jednoduše a rychle **změřit rychlost běžce** mezi dvěma body pomocí videa.  
Budoucím rozšířením může být **detekce kloubních úhlů** (např. dorsiflexe kotníku).

Projekt je navržen tak, aby:
- šel spustit na běžném notebooku
- nevyžadoval velké množství výpočetního výkonu
- byl použitelný i pro trenéry/atlety

---

## Dokumenty

* [How to Run — MediaPipe](how_to_run.md)

---

## Funkce
- **Virtuální brány:** Uživatel definuje start a cíl.
- **Detekce běžce:** Využití MediaPipe Pose pro sledování těžiště (kyčlí).
- **Měření "Zprava do leva" i naopak:** Flexibilní nastavení směru běhu.
- **Čistá vizualizace:** Filtrace nepotřebných bodů (obličej, prsty) pro přehlednější zobrazení techniky.

---

## Použité technologie
- **Python: verze 3.9 - 3.12**, testoval jsem s 3.10
- **OpenCV** — práce s videem
- **MediaPipe Pose** — Robustní model pro detekci kloubů běžce.
- **NumPy** — Výpočty souřadnic.

---

## Aktuální stav projektu
- **Implementováno měření rychlosti:**
  - Program úspěšně měří čas v definovaném úseku (sample video je 10m).
- **Vyřešena kalibrace:**
  - Vytvořen skript pro manuální zadání souřadnic startu a cíle z videa.
- **Optimalizace výkonu:**
  - Možnost přepínání `model_complexity` (1 pro rychlost / 2 pro přesnost).
  - Vyloučení landmarků hlavy a prstů pro čistší vizuál.

<p align="center">
  <img src="/assets/demo.jpg" width="400" alt="Testovací prostředí - zimní stadion">
  <br>
  <em>Testovací prostředí: úsek 10m.</em>
</p>

###  Hardware experimenty
V rámci praxe zkouším akceleraci pomocí platformy **Kria KV260**  
 *(možnost realtime analýzy, více kamer, rychlejší zpracování)*

Odkaz na hardware:  
**Kria KV260 Vision AI Starter Kit**  
https://www.amd.com/en/products/development-tools/kria/kv260

<img src="/assets/kria.jpg" width="300" align="left" alt="Kria KV260">

<br clear="left" />


---

## 👨‍💻 Autor
**Filip Hřivňacký**
