import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Tuple, Optional, List

CONFIG = {
    'page_title': "Diamantanalys – Guldfynd",
    'background_url': "https://i.imgur.com/edBoQCV.jpeg",
    'required_columns': ['carat', 'price', 'cut', 'color', 'clarity'],
    'required_columns2': ['brand', 'model', 'year', 'mileage', 'price'],
    'depth_tolerance': 1.0,
    'length_width_ratio_range': (0.9, 1.1),
    'zero_check_columns': ['carat', 'price', 'x', 'y', 'z']
}


def setup_page_config():
    """Ställer in sidans grundinställningar."""

    st.set_page_config(page_title=CONFIG['page_title'], layout="wide")
    st.title("💎 Diamantanalys för Guldfynd")


def add_background_styling(url: str):
    """Lägger till bakgrundsbild på sidan.
    Args:
        url: Länk till bakgrundsbilden
    """
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


@st.cache_data
def load_excel_data(file) -> Optional[pd.DataFrame]:
    """Laddar Excel-fil och gör grundläggande rensning.
    Args:
        file: Streamlit-filuppladdning
    Returns:
        DataFrame med grundrensning, eller None om det blir fel
    """

    try:
        df = pd.read_excel(file)
        df = df.dropna()
        
        # Ta bort onamngivna indexkolumner
        unnamed_cols = [col for col in df.columns if col.startswith('Unnamed:')]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
            
        return df
    except Exception as e:
        st.error(f"❌ Ett fel uppstod vid inläsning av Excel-filen:\n\n```{e}\n```")
        return None


def calculate_depth_deviation(df: pd.DataFrame) -> pd.DataFrame:
    """Räknar ut djupavvikelse från x, y, z-måtten.
    Args:
        df: DataFrame med x, y, z, depth-kolumner
    Returns:
        DataFrame med tillagda depth_calc och depth_diff kolumner
    """

    df = df.copy()
    df['depth_calc'] = (df['z'] / ((df['x'] + df['y']) / 2)) * 100
    df['depth_diff'] = abs(df['depth_calc'] - df['depth'])
    return df


def clean_diamond_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Rensar diamantdata enligt olika kvalitetsregler.
    Args:
        df: Orensad diamant-DataFrame
    Returns:
        Tuple med (rensad_df, borttagnings_logg)
    """

    df_clean = df.copy()
    removal_log = {}
    
    # 1. Rensa baserat på djupavvikelse
    if all(col in df_clean.columns for col in ['x', 'y', 'z', 'depth']):
        df_clean = calculate_depth_deviation(df_clean)
        before = len(df_clean)
        df_clean = df_clean[df_clean['depth_diff'] <= CONFIG['depth_tolerance']]
        removal_log[f">%{CONFIG['depth_tolerance']} avvikelse i depth"] = before - len(df_clean)
    
    # 2. Rensa längd-bredd förhållande
    if all(col in df_clean.columns for col in ['x', 'y']):
        df_clean['längd_bredd_kvot'] = df_clean['x'] / df_clean['y']
        before = len(df_clean)
        min_ratio, max_ratio = CONFIG['length_width_ratio_range']
        df_clean = df_clean[
            (df_clean['längd_bredd_kvot'] >= min_ratio) & 
            (df_clean['längd_bredd_kvot'] <= max_ratio)
        ]
        removal_log[f'L/B-förhållande utanför {min_ratio}–{max_ratio}'] = before - len(df_clean)
    
    # 3. Ta bort nollvärden i viktiga mått
    zero_check_cols = [col for col in CONFIG['zero_check_columns'] if col in df_clean.columns]
    if zero_check_cols:
        before = len(df_clean)
        df_clean = df_clean[(df_clean[zero_check_cols] != 0).all(axis=1)]
        removal_log['Nollvärden i fysiska mått'] = before - len(df_clean)
    
    return df_clean, removal_log


def display_cleaning_summary(original_count: int, cleaned_count: int, removal_log: Dict[str, int]):
    """Visar sammanfattning av datarensningen.
    Args:
        original_count: Antal rader före rensning
        cleaned_count: Antal rader efter rensning
        removal_log: Ordbok med anledningar och antal borttagna
    """

    removed_total = original_count - cleaned_count
    st.markdown(f"🧹 **Rensning av data:** {removed_total} rader borttagna, {cleaned_count} kvar.")
    
    if removal_log:
        with st.expander("📋 Detaljerad rensningslogg"):
            st.markdown("- **DropNA gjordes vid inläsning av fil (extra säkerhet)**")
            for reason, count in removal_log.items():
                if count > 0:
                    st.markdown(f"- **{reason}**: {count} rader")


def validate_required_columns(selected_columns: List[str]) -> bool:
    """Kollar så att alla nödvändiga kolumner är valda.
    Args:
        selected_columns: Lista med kolumnnamn som användaren valt
    Returns:
        True om alla nödvändiga kolumner finns med
    """

    missing_cols = [col for col in CONFIG['required_columns'] if col not in selected_columns]
    if missing_cols:
        st.error(f"Vänligen inkludera kolumnerna: {', '.join(missing_cols)}")
        return False
    return True

def create_dynamic_filters(df: pd.DataFrame, selected_columns: List[str]) -> Dict:
    """Filter baserat på valda kolumner och datatyper.
    Args:
        df: DataFrame att skapa filter för
        selected_columns: Kolumner att skapa filter för
    Returns:
        Lista med Filter
    """

    filters = {}
    
    for col in selected_columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            filters[col] = st.sidebar.slider(f"{col}", min_val, max_val, (min_val, max_val))
        else:
            unique_vals = df[col].dropna().unique().tolist()
            filters[col] = st.sidebar.multiselect(f"{col}", options=unique_vals, default=unique_vals)
    
    return filters

def apply_filters(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Tillåter filter på DF.
    Args:
        df: DataFrame att filtrera
        filters: Ordbok med filtervillkor
    Returns:
        Filtrerad DataFrame
    """

    filtered_df = df.copy()
    
    for col, filter_val in filters.items():
        if isinstance(filter_val, tuple):  # Numerisk slider
            filtered_df = filtered_df[filtered_df[col].between(*filter_val)]
        else:  # Flerval
            if filter_val:  # Bara om det inte är tomt
                filtered_df = filtered_df[filtered_df[col].isin(filter_val)]
    
    return filtered_df

@st.cache_data
def create_price_carat_scatter(df: pd.DataFrame) -> object:
    """Spridningsdiagram för pris vs karat."""

    return px.scatter(
        df,
        x="carat",
        y="price",
        color="clarity" if "clarity" in df.columns else None,
        symbol="cut" if "cut" in df.columns else None,
        hover_data=[col for col in ['color', 'cut'] if col in df.columns],
        title="Pris i relation till Carat och Kvalitet",
        labels={"carat": "Carat", "price": "Pris (USD)"}
    )

@st.cache_data
def create_avg_price_by_cut(df: pd.DataFrame) -> object:
    """ Stapeldiagram för medelpris per cut."""

    avg_price_cut = df.groupby("cut")["price"].mean().reset_index()
    return px.bar(
        avg_price_cut,
        x="cut",
        y="price",
        title="Genomsnittligt pris per Cut",
        labels={"cut": "Slipkvalitet (Cut)", "price": "Genomsnittligt pris (USD)"},
        color_discrete_sequence=["gold"]
    )

@st.cache_data 
def create_price_histogram(df: pd.DataFrame) -> object:
    """Histogram över prisfördelning."""

    return px.histogram(
        df,
        x="price",
        nbins=30,
        title="Prisdistribution för Diamanter",
        labels={"price": "Pris (USD)", "count": "Antal diamanter"},
        color_discrete_sequence=["skyblue"]
    )


def display_visualizations(df: pd.DataFrame):
    """Visar alla grafer för diamantdatan."""

    if 'carat' in df.columns and 'price' in df.columns:
        st.subheader("📈 Pris per Carat")
        fig1 = create_price_carat_scatter(df)
        st.plotly_chart(fig1, use_container_width=True)

    if 'cut' in df.columns and 'price' in df.columns:
        st.subheader("📊 Genomsnittligt pris per Cut")
        fig2 = create_avg_price_by_cut(df)
        st.plotly_chart(fig2, use_container_width=True)

    if 'price' in df.columns:
        st.subheader("📉 Prisdistribution")
        fig3 = create_price_histogram(df)
        st.plotly_chart(fig3, use_container_width=True)


def perform_analysis(df: pd.DataFrame, analysis_type: str):
    """Utför vald analys på datan.
    Args:
        df: DataFrame att analysera
        analysis_type: Typ av analys som ska göras
    """

    if analysis_type == "Visa filtrerade diamanter":
        st.dataframe(df)
        
    elif analysis_type == "Räkna antal":
        if 'cut' in df.columns:
            count_summary = df.groupby("cut").size().reset_index(name="Antal")
            st.subheader("📂 Antal diamanter per Cut")
            st.dataframe(count_summary)
        
    elif analysis_type == "Summera pris":
        if 'price' in df.columns:
            price_sum = df["price"].sum()
            st.subheader("💰 Total summa (USD)")
            st.metric(label="Totalt pris för valda diamanter", value=f"${price_sum:,.0f}")
            
    elif analysis_type == "Medelpris per cut":
        if all(col in df.columns for col in ['cut', 'price']):
            avg_price = df.groupby("cut")["price"].mean().reset_index()
            avg_price.columns = ["Cut", "Medelpris (USD)"]
            st.subheader("📊 Medelpris per Cut")
            st.dataframe(avg_price)

def main():
    """Huvudfunktion för applikationen."""

    # Grundinställningar
    setup_page_config()
    add_background_styling(CONFIG['background_url'])
    
    # Filuppladdning
    uploaded_file = st.file_uploader("📁 Ladda upp en Excel-fil", type=["xlsx", "xls"])
    
    if uploaded_file is None:
        st.warning("Ingen data kunde laddas. Kontrollera filens innehåll och format.")
        return
    
    # Ladda och rensa data
    with st.spinner("Laddar data..."):
        df = load_excel_data(uploaded_file)
        
    if df is None:
        return
        
    df_clean, removal_log = clean_diamond_data(df)
    display_cleaning_summary(len(df), len(df_clean), removal_log)
    st.success("✅ Fil inläst!")
    
    # Sidopanel med kontroller
    st.sidebar.header("🔍 Filter och Kolumner")
    all_columns = df_clean.columns.tolist()
    selected_columns = st.sidebar.multiselect(
        "Välj kolumner för analys (minst 5 obligatoriska: carat, price, cut, color, clarity)",
        options=all_columns,
        default=all_columns[:5]
    )
    
    if not validate_required_columns(selected_columns):
        st.stop()
    
    # Skapa filter och applicera dem
    filters = create_dynamic_filters(df_clean, selected_columns)
    filtered_df = apply_filters(df_clean, filters)
    
    st.markdown(f"### Filtrerade diamanter: {len(filtered_df)} st")
    
    # Grafer och visualiseringar
    display_visualizations(filtered_df)
    
    st.markdown("---")
    st.markdown("📊 Analysen är baserad på uppladdad data. Visualiseringar med Plotly.")
    
    # Analysalternativ
    st.sidebar.markdown("### 📌 Välj analys")
    analysis_option = st.sidebar.selectbox(
        "Vad vill du analysera?",
        ("Visa filtrerade diamanter", "Räkna antal", "Summera pris", "Medelpris per cut")
    )
    
    perform_analysis(filtered_df, analysis_option)

if __name__ == "__main__":
    main()