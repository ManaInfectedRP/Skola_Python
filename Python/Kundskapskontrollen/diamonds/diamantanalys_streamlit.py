import streamlit as st
import pandas as pd
import plotly.express as px
import os


# --- Sidinställningar ---
st.set_page_config(page_title="Diamantanalys – Guldfynd", layout="wide")
st.title("💎 Diamantanalys för Guldfynd")

# --- Bakgrunds Bild ---
def add_bg_from_url(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_url("https://i.imgur.com/edBoQCV.jpeg")

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
    cols_to_check = ['carat', 'price', 'x', 'y', 'z']
    cols_exist = [col for col in cols_to_check if col in df.columns]

    if cols_exist:
        df = df[(df[cols_exist] != 0).all(axis=1)]

    removed = df.dropna()
# Depth-avvikelse
    df['depth_calc'] = (df['z'] / ((df['x'] + df['y']) / 2)) * 100
    df['depth_diff'] = abs(df['depth_calc'] - df['depth'])
    before = df.shape[0]
    df = df[df['depth_diff'] <= 1]
    removed[">1% avvikelse i depth"] = before - df.shape[0]

    # --- Mappa "cut"-värden ---
    cut_mapping = {
        "Ideal": "Excellent",
        "Premium": "Very Good",
        "Very Good": "Good",
        "Good": "Fair",
        "Fair": "Poor"
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
    st.sidebar.markdown("### 📌 Välj analys")
    analysis_option = st.sidebar.selectbox(
        "Vad vill du analysera?",
        ("Visa filtrerade diamanter", "Räkna antal", "Summera pris", "Medelpris per cut")
    )

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

    st.markdown("---")
    st.markdown("📊 Analysen är baserad på en skoluppgifts diamantdata. Visualiseringar med Plotly.")

    st.markdown(f"### Filtrerade diamanter: {len(filtered_df)} st")

    if analysis_option == "Visa filtrerade diamanter":
        st.dataframe(filtered_df)

    elif analysis_option == "Räkna antal":
        count_summary = filtered_df.groupby("cut_gia").size().reset_index(name="Antal")
        st.subheader("🔢 Antal diamanter per Cut")
        st.dataframe(count_summary)

    elif analysis_option == "Summera pris":
        price_sum = filtered_df["price"].sum()
        st.subheader("💰 Total summa (USD)")
        st.metric(label="Totalt pris för valda diamanter", value=f"${price_sum:,.0f}")

    elif analysis_option == "Medelpris per cut":
        avg_price = filtered_df.groupby("cut_gia")["price"].mean().reset_index()
        avg_price.columns = ["Cut (GIA)", "Medelpris (USD)"]
        st.subheader("📊 Medelpris per Cut")
        st.dataframe(avg_price)


else:
    st.warning("Ingen data kunde laddas. Kontrollera filvägen ovan.")
