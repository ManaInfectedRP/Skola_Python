
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Titel
st.title("💎 Diamantanalys för Guldfynd")
st.markdown("""
Denna interaktiva applikation visar insikter från en analys av diamantpriser baserat på vikt, färg, klarhet och slipkvalitet.
Använd reglage och val för att filtrera och utforska data.
""")

# Läs in data
@st.cache_data
def load_data():
    df = pd.read_excel(r'C:\Users\SebbePwnYou\repos\Skola\Python\Kundskapskontrollen\diamonds\diamonds.xlsx')
    return df.dropna()

df = load_data()

# Filter
carat_min, carat_max = st.slider("Välj carat-intervall:", float(df["carat"].min()), float(df["carat"].max()), (0.5, 1.5))
clarity_options = st.multiselect("Välj klarhet:", options=sorted(df["clarity"].unique()), default=list(sorted(df["clarity"].unique())))
color_options = st.multiselect("Välj färg:", options=sorted(df["color"].unique()), default=list(sorted(df["color"].unique())))

# Filtrera data
filtered_df = df[
    (df["carat"] >= carat_min) &
    (df["carat"] <= carat_max) &
    (df["clarity"].isin(clarity_options)) &
    (df["color"].isin(color_options))
]

st.write(f"Visar {len(filtered_df)} rader efter filter.")

# Pris vs Carat scatterplot
fig1, ax1 = plt.subplots()
ax1.scatter(filtered_df["carat"], filtered_df["price"], alpha=0.5)
ax1.set_title("Pris vs Carat")
ax1.set_xlabel("Carat")
ax1.set_ylabel("Pris (USD)")
st.pyplot(fig1)

# Genomsnittligt pris per färg
avg_color = filtered_df.groupby("color")["price"].mean().sort_index()
fig2, ax2 = plt.subplots()
# Färgkarta för diamantfärger
color_map = {
    'D': '#4B9CD3',
    'E': '#76B041',
    'F': '#FFD700',
    'G': '#FF7F50',
    'H': '#D87093',
    'I': '#9370DB',
    'J': '#A9A9A9'
}

bar_colors = [color_map.get(color, 'gray') for color in avg_color.index]
ax2.bar(avg_color.index, avg_color.values, color=bar_colors)

ax2.set_title("Genomsnittligt pris per färg")
ax2.set_xlabel("Färg")
ax2.set_ylabel("Pris (USD)")
st.pyplot(fig2)

# Genomsnittligt pris per klarhet
avg_clarity = filtered_df.groupby("clarity")["price"].mean().sort_index()
fig3, ax3 = plt.subplots()
ax3.bar(avg_clarity.index, avg_clarity.values, color="silver")
ax3.set_title("Genomsnittligt pris per klarhet")
ax3.set_xlabel("Klarhet")
ax3.set_ylabel("Pris (USD)")
st.pyplot(fig3)
