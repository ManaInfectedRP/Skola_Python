import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- Sidinställningar ---
st.set_page_config(page_title="🔗 Korrelationer – Diamanter", layout="wide")

# --- Ladda och rensa data ---
@st.cache_data
def load_data():
    df = pd.read_excel(r'C:\Users\SebbePwnYou\repos\Skola\Python\Kundskapskontrollen\diamonds\diamonds.xlsx')
    return df.dropna()

df = load_data()

# --- Titel ---
st.title("🔗 Korrelationer mellan Diamantegenskaper")


# --- Numeriska kolumner ---
numeriska_kolumner = df.select_dtypes(include=np.number).columns.tolist()

# --- Korrelationstabell ---
corr_matrix = df[numeriska_kolumner].corr()

st.subheader("📋 Korrelationstabell")
st.dataframe(corr_matrix.round(2), use_container_width=True)

# --- Plotly Heatmap ---
st.subheader("🌡️ Interaktiv Heatmap med Plotly")
# Skapa heatmap med värden i varje ruta
fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=corr_matrix.values,
        x=numeriska_kolumner,
        y=numeriska_kolumner,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        colorbar=dict(title="Korrelationsvärde"),
        hoverinfo="z",
        showscale=True
    )
)

# Lägg till text i varje ruta (värdet)
for i in range(len(corr_matrix)):
    for j in range(len(corr_matrix.columns)):
        fig_heatmap.add_annotation(
            text=f"{corr_matrix.values[i][j]:.2f}",
            x=corr_matrix.columns[j],
            y=corr_matrix.index[i],
            showarrow=False,
            font=dict(color="black", size=12)
        )

fig_heatmap.update_layout(
    title="🌡️ Korrelationer mellan numeriska variabler",
    xaxis=dict(
        tickangle=-45,
        side="bottom"
    ),
    yaxis=dict(
        autorange="reversed"
    ),
    width=800,
    height=800,
    font=dict(size=12),
    margin=dict(l=100, r=100, t=50, b=50)
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# --- Välj två variabler och visa korrelation + scatter ---
st.subheader("🎯 Korrelation mellan två valda egenskaper")
col1, col2 = st.columns(2)
with col1:
    val_x = st.selectbox("Välj första variabel", numeriska_kolumner, index=0)
with col2:
    val_y = st.selectbox("Välj andra variabel", numeriska_kolumner, index=1)

korrelation = df[[val_x, val_y]].corr().iloc[0, 1]
st.metric(label=f"Korrelation mellan {val_x} och {val_y}", value=f"{korrelation:.2f}")

# --- Plotly Scatterplot ---
fig_scatter = px.scatter(
    df,
    x=val_x,
    y=val_y,
    opacity=0.5,
    title=f"{val_x} vs {val_y}",
    labels={val_x: val_x, val_y: val_y},
    width=1200,  # Set desired width in pixels
    height=700   # Set desired height in pixels
)
st.plotly_chart(fig_scatter, use_container_width=False)


# --- Footer ---
st.markdown("---")