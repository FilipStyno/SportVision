# SportVision — jednoduchá analýza sportu z videa

<p align="center"><em>Krátký školní projekt zaměřený na analýzu pohybu sportovce z běžného videa.</em></p>


<p align="center">
  <img src="assets/pose.png" width="600" alt="Ukázka aplikace">
</p>

##  Cíl projektu
Jednoduše a rychle **změřit rychlost běžce** mezi dvěma body pomocí videa.  
Budoucím rozšířením může být **detekce kloubních úhlů** (např. dorsiflexe kotníku).

Projekt je navržen tak, aby:
- šel spustit na běžném notebooku
- nevyžadoval velké množství výpočetního výkonu
- byl použitelný i pro trenéry/atlety

---

##  Funkce
- Nahrání videa (`.mp4`)
- Detekce postavy (pose estimation)
- Výpočet základních metrik (např. rychlost)
- Jednoduchý **overlay** v obrazu
- Export dat do `.csv`

---

##  Použité technologie
- **Python 3.13** *(verze může být upravena podle modelů)*
- **OpenCV** — práce s videem
- **MediaPipe / OpenPose / YOLOv11** — testované modely pro detekci postavy

---

##  Aktuální stav projektu
- Proběhla **analýza modelů pro pose estimation**.
  - Hodnotil jsem zejména **přesnost detekce** a **náročnost na hardware**.
- **MediaPipe** se ukázal jako nejvhodnější kompromis mezi rychlostí a přesností.
- Teď se zaměřuji na **měření rychlosti atleta na předem známé vzdálenosti**.
  - Sbírám videa s přesně definovanými body / značkami v prostoru.

###  Hardware experimenty
V rámci praxe zkouším akceleraci pomocí platformy **Kria KV260**  
 *(možnost realtime analýzy, více kamer, rychlejší zpracování)*

Odkaz na hardware:  
**Kria KV260 Vision AI Starter Kit**  
https://www.amd.com/en/products/development-tools/kria/kv260

<img src="assets/kria.jpg" width="300" align="left" alt="Kria KV260">

<br clear="left" />


---

##  Autor
**Filip Hřivňacký**
