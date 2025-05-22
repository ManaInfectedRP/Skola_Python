import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Excel-Visualizer", layout="wide")
st.title("Excel Data Visualizer med Filter & Färgval 🎨")

# 1. Ladda upp Excel-fil
uploaded_file = st.file_uploader("📁 Ladda upp en Excel-fil", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Fil inläst!")

        # Visa dataframe
        st.subheader("📋 Förhandsvisning av data")
        st.dataframe(df.head())

        columns = df.columns.tolist()

        # 2. Filtrera data baserat på kolumnvärden
        st.subheader("🔍 Filtrera data (valfritt)")

        filter_column = st.selectbox("Välj kolumn att filtrera på (eller hoppa över)", ["Ingen"] + columns)

        if filter_column != "Ingen":
            unique_vals = df[filter_column].dropna().unique().tolist()
            selected_vals = st.multiselect(f"Välj värde(n) för '{filter_column}'", unique_vals, default=unique_vals)
            df = df[df[filter_column].isin(selected_vals)]

        # 3. Dropdown för x- och y-axel
        st.subheader("📊 Välj X och Y")
        x_col = st.selectbox("X-axel", columns)
        y_col = st.selectbox("Y-axel", columns)

        # 4. Diagramtyp
        plot_type = st.radio("📈 Välj diagramtyp", ["Scatter", "Line", "Bar"])

        # 5. Färgval
        color = st.color_picker("🎨 Välj färg", "#1f77b4")

        # 6. Rita diagram
        st.subheader("📌 Resultat")
        fig, ax = plt.subplots(figsize=(8, 5))

        if plot_type == "Scatter":
            ax.scatter(df[x_col], df[y_col], color=color)
        elif plot_type == "Line":
            ax.plot(df[x_col], df[y_col], color=color)
        elif plot_type == "Bar":
            ax.bar(df[x_col], df[y_col], color=color)

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{plot_type} Plot: {y_col} vs {x_col}")

        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Fel vid inläsning: {e}")
