import streamlit as st
import pandas as pd
import plotly.express as px

# --- Sidinställningar ---
st.set_page_config(page_title="Diamantanalys – Guldfynd", layout="wide")
st.title("💎 Diamantanalys för Guldfynd")

# --- Bakgrundsbild ---
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

# --- Ladda upp fil ---
uploaded_file = st.file_uploader("📁 Ladda upp en Excel-fil", type=["xlsx", "xls"])

with st.spinner("Laddar data..."):
    @st.cache_data
    def load_data(file):
        try:
            df = pd.read_excel(file)
            df = df.dropna()
            if 'Unnamed: 0' in df.columns:
                df = df.drop(columns=['Unnamed: 0'])
            return df
        except Exception as e:
            st.error(f"❌ Ett fel uppstod vid inläsning av Excel-filen:\n\n```{e}\n```")
            return None

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.success("✅ Fil inläst!")
    else:
        df = None

if df is not None:
    st.sidebar.header("🔍 Filter och Kolumner")
    all_columns = df.columns.tolist()

    carat_col = st.sidebar.selectbox("Kolumn för Carat", options=all_columns)
    price_col = st.sidebar.selectbox("Kolumn för Pris", options=all_columns)
    cut_col = st.sidebar.selectbox("Kolumn för Cut", options=all_columns)
    color_col = st.sidebar.selectbox("Kolumn för Color", options=all_columns)
    clarity_col = st.sidebar.selectbox("Kolumn för Clarity", options=all_columns)
    x_col = st.sidebar.selectbox("Kolumn för X", options=all_columns)
    y_col = st.sidebar.selectbox("Kolumn för Y", options=all_columns)
    z_col = st.sidebar.selectbox("Kolumn för Z", options=all_columns)
    depth_col = st.sidebar.selectbox("Kolumn för Depth", options=all_columns)

    required_columns = [carat_col, price_col, cut_col, color_col, clarity_col, x_col, y_col, z_col, depth_col]
    if not all(col in df.columns for col in required_columns):
        st.error("🚫 Några av de valda kolumnerna finns inte i filen.")
        st.stop()

    df['depth_calc'] = (df[z_col] / ((df[x_col] + df[y_col]) / 2)) * 100
    df['depth_diff'] = abs(df['depth_calc'] - df[depth_col])
    df = df[df['depth_diff'] <= 1]

    cut_mapping = {
        "Ideal": "Excellent",
        "Premium": "Very Good",
        "Very Good": "Good",
        "Good": "Fair",
        "Fair": "Poor"
    }
    df["cut_gia"] = df[cut_col].map(cut_mapping)

    carat_range = st.sidebar.slider("Carat", float(df[carat_col].min()), float(df[carat_col].max()), (0.5, 1.5))
    selected_cut = st.sidebar.multiselect("Cut (GIA)", options=df['cut_gia'].dropna().unique(), default=list(df['cut_gia'].dropna().unique()))
    selected_color = st.sidebar.multiselect("Color", options=df[color_col].unique(), default=list(df[color_col].unique()))
    selected_clarity = st.sidebar.multiselect("Clarity", options=df[clarity_col].unique(), default=list(df[clarity_col].unique()))

    st.sidebar.markdown("### 📌 Välj analys")
    analysis_option = st.sidebar.selectbox(
        "Vad vill du analysera?",
        ("Visa filtrerade diamanter", "Räkna antal", "Summera pris", "Medelpris per cut")
    )

    filtered_df = df[
        (df[carat_col].between(*carat_range)) &
        (df["cut_gia"].isin(selected_cut)) &
        (df[color_col].isin(selected_color)) &
        (df[clarity_col].isin(selected_clarity))
    ]

    st.markdown(f"### Filtrerade diamanter: {len(filtered_df)} st")

    # --- Visualiseringar ---
    st.subheader("📈 Pris per Carat")
    fig1 = px.scatter(
        filtered_df,
        x=carat_col,
        y=price_col,
        color=clarity_col,
        symbol=cut_col,
        hover_data=[color_col, cut_col],
        title="Pris i relation till Carat och Kvalitet",
        labels={carat_col: "Carat", price_col: "Pris (USD)"}
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 Genomsnittligt pris per Cut")
    avg_price_cut = filtered_df.groupby("cut_gia")[price_col].mean().reset_index()
    avg_price_cut = avg_price_cut.rename(columns={"cut_gia": "cut"})
    fig2 = px.bar(
        avg_price_cut,
        x="cut",
        y=price_col,
        title="Genomsnittligt pris per Cut",
        labels={"cut": "Slipkvalitet (Cut)", price_col: "Genomsnittligt pris (USD)"},
        color_discrete_sequence=["gold"]
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📉 Prisdistribution")
    fig3 = px.histogram(
        filtered_df,
        x=price_col,
        nbins=30,
        title="Prisdistribution för Diamanter",
        labels={price_col: "Pris (USD)", "count": "Antal diamanter"},
        color_discrete_sequence=["skyblue"]
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown("📊 Analysen är baserad på uppladdad data. Visualiseringar med Plotly.")

    if analysis_option == "Visa filtrerade diamanter":
        st.dataframe(filtered_df)

    elif analysis_option == "Räkna antal":
        count_summary = filtered_df.groupby("cut_gia").size().reset_index(name="Antal")
        st.subheader("📂 Antal diamanter per Cut")
        st.dataframe(count_summary)

    elif analysis_option == "Summera pris":
        price_sum = filtered_df[price_col].sum()
        st.subheader("💰 Total summa (USD)")
        st.metric(label="Totalt pris för valda diamanter", value=f"${price_sum:,.0f}")

    elif analysis_option == "Medelpris per cut":
        avg_price = filtered_df.groupby("cut_gia")[price_col].mean().reset_index()
        avg_price.columns = ["Cut (GIA)", "Medelpris (USD)"]
        st.subheader("📊 Medelpris per Cut")
        st.dataframe(avg_price)

else:
    st.warning("Ingen data kunde laddas. Kontrollera filens innehåll och format.")