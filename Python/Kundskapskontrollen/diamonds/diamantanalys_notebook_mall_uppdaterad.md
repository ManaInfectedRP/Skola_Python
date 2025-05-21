
# 💎 Diamantanalyser för Guldfynd – Affärsinsikter inför sortimentsutvidgning

## 📌 Inledning
Guldfynd, med butiker över hela Norden, överväger att utöka sitt sortiment till att även inkludera diamanter.
Syftet med denna analys är att undersöka diamantmarknaden genom ett tillgängligt dataset för att förstå vad som påverkar priset,
och ge rekommendationer kring vilka diamanttyper som kan vara kommersiellt mest attraktiva att sälja.

---

## 🧹 Datapreparation
Vi börjar med att ladda in datan, undersöka dess struktur och rensa bort saknade värden för att möjliggöra en pålitlig analys.

```python
import pandas as pd
import numpy as np

# Läs in data
df = pd.read_excel("diamonds.xlsx")

# Rensa bort rader med saknade värden
df_clean = df.dropna()

# Visa grundläggande information
df_clean.info()
df_clean.head()
```

---

## 📊 Explorativ Dataanalys med Matplotlib

### 📈 1. Pris vs Vikt (Carat)
```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
plt.scatter(df_clean["carat"], df_clean["price"], alpha=0.4)
plt.title("Pris vs Vikt (Carat)")
plt.xlabel("Carat")
plt.ylabel("Pris (USD)")
plt.show()
```

**🧠 Insikt:** Priset ökar med karat, men inte linjärt. Större diamanter har oproportionerligt högre pris.

---

### 🎨 2. Genomsnittligt Pris per Färg
```python
avg_price_by_color = df_clean.groupby("color")["price"].mean().sort_index()
plt.figure(figsize=(10,6))
plt.bar(avg_price_by_color.index, avg_price_by_color.values, color="gold")
plt.title("Genomsnittligt Pris per Färg")
plt.xlabel("Färg")
plt.ylabel("Pris (USD)")
plt.show()
```

**🧠 Insikt:** Färger närmare D är generellt dyrare. G-H verkar vara en bra balans mellan pris och färgkvalitet.

---

### 🔍 3. Genomsnittligt Pris per Klarhet
```python
avg_price_by_clarity = df_clean.groupby("clarity")["price"].mean().sort_index()
plt.figure(figsize=(10,6))
plt.bar(avg_price_by_clarity.index, avg_price_by_clarity.values, color="silver")
plt.title("Genomsnittligt Pris per Klarhet")
plt.xlabel("Klarhet")
plt.ylabel("Pris (USD)")
plt.show()
```

**🧠 Insikt:** Klarhetstyper som VVS1, IF är dyrast. VS2–SI1 är intressanta för pris/prestanda.

---

### 💎 4. Genomsnittligt Pris per Slipkvalitet (Cut)
```python
avg_price_by_cut = df_clean.groupby("cut")["price"].mean().sort_index()
plt.figure(figsize=(10,6))
plt.bar(avg_price_by_cut.index, avg_price_by_cut.values, color="green")
plt.title("Genomsnittligt Pris per Slipkvalitet (Cut)")
plt.xlabel("Slipkvalitet")
plt.ylabel("Pris (USD)")
plt.show()
```

**🧠 Insikt:** Slipkvalitet påverkar pris men mindre än klarhet och färg. Premium och Ideal är något dyrare.

---

## 🧠 Sammanfattande Insikter

- Pris påverkas starkt av **carat**, följt av **klarhet** och **färg**.
- Slipkvalitet spelar roll men är inte den starkaste prisfaktorn.
- Det finns möjligheter att hitta värdefulla kombinationer i mellansegmentet (t.ex. 0.7 carat, VS2, färg G).

---

## 📝 Executive Summary

**Förslag till Guldfynds ledning:**

- Fokusera initialt på diamanter i intervallet **0.5–1.0 carat**, där prisskillnader är tydliga men inte extrema.
- Välj **klarhet VS1–SI1** och **färg G–H**, där balansen mellan pris och kvalitet är stark.
- Undvik mycket små (<0.3 carat) eller mycket dyra (>2 carat) stenar i ett första sortiment.
- Kombinera diamantförsäljning med pedagogisk kundkommunikation kring vad som påverkar pris (carat, klarhet, färg).

---

## 📦 Nästa Steg: Streamlit App
Bygg en enklare interaktiv app som visar de viktigaste graferna och låter användaren filtrera efter vikt, färg eller klarhet.
