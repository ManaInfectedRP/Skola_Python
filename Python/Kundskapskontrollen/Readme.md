# 💎 Diamantanalys – Streamlit-app för Guldfynd

Den här applikationen låter dig ladda upp en Excel-fil med diamantdata, filtrera och visualisera olika aspekter som pris, vikt (carat), slipkvalitet (cut), färg (color) och klarhet (clarity). Appen utför också automatisk rensning av orimliga värden baserat på fysiska egenskaper.

https://diamantanalys.streamlit.app/

---

## 🧰 Funktioner

- 📤 Ladda upp Excel-filer (`.xlsx` eller `.xls`)
- 🔍 Filtrera data efter valda kolumner och värden
- 📈 Visualisera pris per carat, histogram över prisfördelning m.m.
- 🧹 Automatisk datarensning baserat på:
  - Depth-avvikelse (z i förhållande till x och y)
  - Table-procent (förhållande mellan table och diameter)
  - Längd–bredd-förhållande (x/y)
  - Nollvärden i dimensioner
- 📊 Interaktiv analys: summera pris, räkna antal eller visa medelvärden

---

## 📂 Krav

- Python 3.8+
- Nödvändiga Python-bibliotek:

```bash
pip install streamlit pandas openpyxl plotly
