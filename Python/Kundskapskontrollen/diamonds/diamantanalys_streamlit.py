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

    selected_columns = st.sidebar.multiselect("Välj kolumner för analys (minst 5 obligatoriska: carat, price, cut, color, clarity)", options=all_columns, default=all_columns[:5])

    if not all(col in selected_columns for col in ['carat', 'price', 'cut', 'color', 'clarity']):
        st.error("Vänligen inkludera minst kolumnerna: carat, price, cut, color, clarity.")
        st.stop()

    # --- Dynamiska filter baserat på valda kolumner ---
    filters = {}
    for col in selected_columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            filters[col] = st.sidebar.slider(f"{col}", min_val, max_val, (min_val, max_val))
        else:
            unique_vals = df[col].dropna().unique().tolist()
            filters[col] = st.sidebar.multiselect(f"{col}", options=unique_vals, default=unique_vals)

    # --- Filtrera datan ---
    filtered_df = df.copy()
    for col, filter_val in filters.items():
        if isinstance(filter_val, tuple):
            filtered_df = filtered_df[filtered_df[col].between(*filter_val)]
        else:
            filtered_df = filtered_df[filtered_df[col].isin(filter_val)]

    st.markdown(f"### Filtrerade diamanter: {len(filtered_df)} st")

    # --- Visualiseringar ---
    if 'carat' in filtered_df.columns and 'price' in filtered_df.columns:
        st.subheader("📈 Pris per Carat")
        fig1 = px.scatter(
            filtered_df,
            x="carat",
            y="price",
            color="clarity" if "clarity" in filtered_df.columns else None,
            symbol="cut" if "cut" in filtered_df.columns else None,
            hover_data=[col for col in ['color', 'cut'] if col in filtered_df.columns],
            title="Pris i relation till Carat och Kvalitet",
            labels={"carat": "Carat", "price": "Pris (USD)"}
        )
        st.plotly_chart(fig1, use_container_width=True)

    if 'cut' in filtered_df.columns and 'price' in filtered_df.columns:
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

    if 'price' in filtered_df.columns:
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
    st.markdown("📊 Analysen är baserad på uppladdad data. Visualiseringar med Plotly.")

    # --- Analysval ---
    st.sidebar.markdown("### 📌 Välj analys")
    analysis_option = st.sidebar.selectbox(
        "Vad vill du analysera?",
        ("Visa filtrerade diamanter", "Räkna antal", "Summera pris", "Medelpris per cut")
    )

    if analysis_option == "Visa filtrerade diamanter":
        st.dataframe(filtered_df)

    elif analysis_option == "Räkna antal":
        count_summary = filtered_df.groupby("cut").size().reset_index(name="Antal")
        st.subheader("📂 Antal diamanter per Cut")
        st.dataframe(count_summary)

    elif analysis_option == "Summera pris":
        price_sum = filtered_df["price"].sum()
        st.subheader("💰 Total summa (USD)")
        st.metric(label="Totalt pris för valda diamanter", value=f"${price_sum:,.0f}")

    elif analysis_option == "Medelpris per cut":
        avg_price = filtered_df.groupby("cut")["price"].mean().reset_index()
        avg_price.columns = ["Cut", "Medelpris (USD)"]
        st.subheader("📊 Medelpris per Cut")
        st.dataframe(avg_price)

else:
    st.warning("Ingen data kunde laddas. Kontrollera filens innehåll och format.")
