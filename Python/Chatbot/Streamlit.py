import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Excel Visualizer", layout="wide")
st.title("📊 Excel Data Visualizer med Arkval, Filter & Färg")

# 1. Ladda upp Excel-fil
uploaded_file = st.file_uploader("📁 Ladda upp en Excel-fil", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # 2. Lista alla ark i Excel-filen
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        sheet = st.selectbox("🗂️ Välj ark i Excel-filen", sheet_names)

        # 3. Läs valt ark
        df = pd.read_excel(excel_file, sheet_name=sheet)
        st.success(f"✅ Ark '{sheet}' inläst!")

        # Visa dataframe
        st.subheader("📋 Förhandsvisning av data")
        st.dataframe(df.head())

        columns = df.columns.tolist()

        # 4. Välj X- och Y-kolumner
        st.subheader("📊 Välj kolumner för graf")
        x_col = st.selectbox("X-axel", columns)
        y_col = st.selectbox("Y-axel", columns)

        # 5. Välj typ av diagram
        plot_type = st.radio("📈 Välj diagramtyp", ["Scatter", "Line", "Bar"])

        # 6. Färgval
        color = st.color_picker("🎨 Välj färg", "#1f77b4")

        # 7. Visa graf
        st.subheader("📌 Diagram")
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
