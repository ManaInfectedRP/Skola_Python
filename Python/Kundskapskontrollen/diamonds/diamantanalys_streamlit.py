import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Sidinställningar ---
st.set_page_config(page_title="Diamantanalys – Guldfynd", layout="wide")
st.title("💎 Diamantanalys för Guldfynd")

# 1. Ladda upp Excel-fil
uploaded_file = st.file_uploader("📁 Ladda upp en Excel-fil", type=["xlsx", "xls"])

# --- Laddningsindikator ---
with st.spinner("Laddar data..."):
    @st.cache_data
    def load_data(file):
        try:
            df = pd.read_excel(file)
            return df.dropna()
        except Exception as e:
            st.error(f"❌ Ett fel uppstod vid inläsning av Excel-filen:\n\n```\n{e}\n```")
            return None

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.success("✅ Fil inläst!")
    else:
        df = None

if df is not None:
    # --- Mappa "cut"-värden ---
    cut_mapping = {
        "Ideal": "Excellent",
        "Premium": "Mellan Ex o VG",
        "Very Good": "Very Good",
        "Good": "Good",
        "Fair": "Fair"
    }
    df["cut_gia"] = df["cut"].map(cut_mapping)

    # --- Introduktion ---
    st.markdown("""
    Välkommen till Guldfynds diamantanalysverktyg.  
    Här kan du utforska diamantdata och få affärsinsikter som kan stödja beslutet att utöka sortimentet.
    """)

    # --- Sidopanel för filter ---
    st.sidebar.header("🔍 Filter")
    carat_range = st.sidebar.slider("Carat", float(df['carat'].min()), float(df['carat'].max()), (0.5, 1.5))
    selected_cut = st.sidebar.multiselect("Cut (GIA)", options=df['cut_gia'].unique(), default=list(df['cut_gia'].unique()))
    selected_color = st.sidebar.multiselect("Color", options=df['color'].unique(), default=list(df['color'].unique()))
    selected_clarity = st.sidebar.multiselect("Clarity", options=df['clarity'].unique(), default=list(df['clarity'].unique()))

    # --- Filtrering ---
    filtered_df = df[
        (df['carat'].between(*carat_range)) &
        (df['cut_gia'].isin(selected_cut)) &
        (df['color'].isin(selected_color)) &
        (df['clarity'].isin(selected_clarity))
    ]

    st.markdown(f"### Filtrerade diamanter: {len(filtered_df)} st")

    # --- Visualisering 1 ---
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

    # --- Visualisering 2 ---
    st.subheader("📊 Genomsnittligt pris per Cut")
    avg_price_cut = filtered_df.groupby("cut_gia")["price"].mean().reset_index()
    avg_price_cut = avg_price_cut.rename(columns={"cut_gia": "cut"})
    fig2 = px.bar(
        avg_price_cut,
        x="cut",
        y="price",
        title="Genomsnittligt pris per Cut",
        labels={"cut": "Slipkvalitet (Cut)", "price": "Genomsnittligt pris (USD)"},
        color_discrete_sequence=["gold"]
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- Visualisering 3 ---
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

    # --- Rekommendationer ---
    st.subheader("📌 Rekommendationer – Executive Summary")
    st.markdown("""
    - **Fokusera på diamanter mellan 0.7 – 1.2 carat**, där marginalerna verkar vara bäst.
    - **Clarity VS2–SI1** och **color G–H** ger bäst balans mellan pris och kvalitet.
    - **Ideal och Very Good cut** rekommenderas då de ofta erbjuder hög kvalitet till rimligt pris.
    - Mellan Ex o VG cut ger ibland högt pris utan proportionellt högre värde.
    - Undvik mycket stora diamanter (>2 carat) i första skedet – dessa är få och dyra.
    """)

    st.markdown("---")
    st.markdown("📊 Analysen är baserad på publikt diamantdata. Visualiseringar med Plotly & Matplotlib.")

else:
    st.warning("Ingen data kunde laddas. Kontrollera filvägen ovan.")
