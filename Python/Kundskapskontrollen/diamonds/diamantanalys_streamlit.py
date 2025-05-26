import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# --- Sidinställningar ---
st.set_page_config(page_title="Diamantanalys – Guldfynd", layout="wide")

# --- Ladda data ---
@st.cache_data
def load_data():
    df = pd.read_excel(r'C:\Users\SebbePwnYou\repos\Skola\Python\Kundskapskontrollen\diamonds\diamonds.xlsx')
    return df.dropna()

df = load_data()

# --- Titel och introduktion ---
st.title("💎 Diamantanalys för Guldfynd")
st.markdown("""
Välkommen till Guldfynds diamantanalysverktyg.  
Här kan du utforska diamantdata och få affärsinsikter som kan stödja beslutet att utöka sortimentet.
""")

# --- Sidopanel för filtrering ---
st.sidebar.header("🔍 Filter")
carat_range = st.sidebar.slider("Carat", float(df['carat'].min()), float(df['carat'].max()), (0.5, 1.5))
selected_cut = st.sidebar.multiselect("Cut", options=df['cut'].unique(), default=list(df['cut'].unique()))
selected_color = st.sidebar.multiselect("Color", options=df['color'].unique(), default=list(df['color'].unique()))
selected_clarity = st.sidebar.multiselect("Clarity", options=df['clarity'].unique(), default=list(df['clarity'].unique()))

# --- Filtrering ---
filtered_df = df[
    (df['carat'].between(*carat_range)) &
    (df['cut'].isin(selected_cut)) &
    (df['color'].isin(selected_color)) &
    (df['clarity'].isin(selected_clarity))
]

st.markdown(f"### Filtrerade diamanter: {len(filtered_df)} st")


st.write(f"Totalt antal rader i datan: {len(df)}")
st.write(f"Antal rader efter dropna: {len(df.dropna())}")
st.write(f"Antal rader efter filter: {len(filtered_df)}")

# --- Visualisering 1: Pris per Carat ---
st.subheader("📈 Pris per Carat")
fig1 = px.scatter(
    filtered_df,
    x="carat",
    y="price",
    color="clarity",
    symbol="cut",
    hover_data=["color", "cut"],
    title="Pris i relation till Carat och Kvalitet",
    labels={"carat": "Carat", "price": "Pris (USD)"}
)
st.plotly_chart(fig1, use_container_width=True)


# --- Visualisering 2: Genomsnittligt pris per Cut ---
st.subheader("📊 Genomsnittligt pris per Cut")
avg_price_cut = filtered_df.groupby("cut")["price"].mean().reset_index()
fig2 = px.bar(
    avg_price_cut,
    x="cut",
    y="price",
    title="Genomsnittligt pris per Cut",
    labels={"cut": "Slipkvalitet (Cut)", "price": "Genomsnittligt pris (USD)"},
    color_discrete_sequence=["gold"]
)
st.plotly_chart(fig2, use_container_width=True)


# --- Visualisering 3: Prisfördelning ---
st.subheader("📉 Prisdistribution")
fig3 = px.histogram(
    filtered_df,
    x="price",
    nbins=30,
    title="Prisdistribution för Diamanter",
    labels={"price": "Pris (USD)", "count": "Antal diamanter"},
    color_discrete_sequence=["skyblue"]
)
st.plotly_chart(fig3, use_container_width=True)


# --- Executive Summary ---
st.subheader("📌 Rekommendationer – Executive Summary")
st.markdown("""
- **Fokusera på diamanter mellan 0.7 – 1.2 carat**, där marginalerna verkar vara bäst.
- **Clarity VS2–SI1** och **color G–H** ger bäst balans mellan pris och kvalitet.
- **Ideal och Very Good cut** rekommenderas då de ofta erbjuder hög kvalitet till rimligt pris.
- Premium cut ger ibland högt pris utan proportionellt högre värde.
- Undvik mycket stora diamanter (>2 carat) i första skedet – dessa är få och dyra.
""")

# --- Footer ---
st.markdown("---")
st.markdown("📊 Analysen är baserad på publikt diamantdata. Visualiseringar med Plotly & Matplotlib.")
