
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Titel och beskrivning
st.title("💎 Guldfynd - Diamantanalys")
st.markdown("Interaktiv applikation för att analysera diamantdata och identifiera affärsmöjligheter.")

# Läs in datan
@st.cache_data
def load_data():
    df = pd.read_excel(r'C:\Users\SebbePwnYou\repos\Skola\Python\Kundskapskontrollen\diamonds\diamonds.xlsx')
    return df.dropna()

df = load_data()

# Filter
carat_range = st.slider("Välj Carat-intervall", float(df["carat"].min()), float(df["carat"].max()), (0.5, 1.5))
clarity_options = st.multiselect("Välj Klarhet", df["clarity"].unique(), default=list(df["clarity"].unique()))
color_options = st.multiselect("Välj Färg", df["color"].unique(), default=list(df["color"].unique()))

# Filtrera data
filtered_df = df[
    (df["carat"] >= carat_range[0]) &
    (df["carat"] <= carat_range[1]) &
    (df["clarity"].isin(clarity_options)) &
    (df["color"].isin(color_options))
]

st.write(f"Antal valda diamanter: {len(filtered_df)}")

# Pris vs Carat
fig1, ax1 = plt.subplots()
ax1.scatter(filtered_df["carat"], filtered_df["price"], alpha=0.5)
ax1.set_xlabel("Carat")
ax1.set_ylabel("Pris (USD)")
ax1.set_title("Pris vs Carat")
st.pyplot(fig1)

# Pris vs Antal (histogram)
fig2, ax2 = plt.subplots()
ax2.hist(filtered_df["price"], bins=30, color="skyblue", edgecolor="black")
ax2.set_title("Prisfördelning")
ax2.set_xlabel("Pris (USD)")
ax2.set_ylabel("Antal")
st.pyplot(fig2)

# Cut Pie Chart
cut_counts = filtered_df["cut"].value_counts()
fig3, ax3 = plt.subplots()
ax3.pie(cut_counts.values, labels=cut_counts.index, autopct="%1.1f%%", startangle=90)
ax3.set_title("Fördelning av Slipkvalitet (Cut)")
ax3.axis("equal")
st.pyplot(fig3)
