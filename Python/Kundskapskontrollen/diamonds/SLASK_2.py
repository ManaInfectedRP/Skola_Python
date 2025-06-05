
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Läs in datan och ta bort rader med saknade värden
df = pd.read_excel('diamonds.xlsx')
df_clean = df.dropna()
cols_to_check = ['carat', 'price', 'x', 'y', 'z']
cols_exist = [col for col in cols_to_check if col in df_clean.columns]

if cols_exist:
    df_clean = df_clean[(df_clean[cols_exist] != 0).all(axis=1)]

antal_före = len(df)
antal_efter = len(df.dropna())
print(f"Antal borttagna rader: {antal_före - antal_efter}")
print(f"Antal rader kvar: {antal_efter}")
df_clean.head()

# Pris x Antal (mörk stil)
price_distribution = df_clean["price"].value_counts().sort_index()
fig7 = go.Figure(data=[
    go.Bar(x=price_distribution.index, y=price_distribution.values,
           marker_color='lightblue')
])
fig7.update_layout(title="Pris x Antal",
                   xaxis_title="Pris (USD)",
                   yaxis_title="Antal",
                   template="plotly_dark",
                   height=500, width=1000)
fig7.show()

# Carat x Antal (mörk stil)
carat_distribution = df_clean["carat"].value_counts().sort_index()
fig8 = go.Figure(data=[
    go.Bar(x=carat_distribution.index, y=carat_distribution.values,
           marker_color='lightblue')
])
fig8.update_layout(title="Carat x Antal",
                   xaxis_title="Carat",
                   yaxis_title="Antal",
                   template="plotly_dark",
                   height=500, width=1000)
fig8.show()


import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Scatter: Pris vs Carat
scatter_trace = go.Scatter(
    x=df_clean["carat"],
    y=df_clean["price"],
    mode='markers',
    marker=dict(opacity=0.4),
    name="Pris vs Vikt"
)

# Pris per Färg
color_map = {
    'D': '#4B9CD3', 'E': '#76B041', 'F': '#FFD700',
    'G': '#FF7F50', 'H': '#D87093', 'I': '#9370DB', 'J': '#A9A9A9'
}
bar_color_trace = go.Bar(
    x=avg_price_by_color.index,
    y=avg_price_by_color.values,
    marker_color=[color_map.get(c, "gray") for c in avg_price_by_color.index],
    name="Pris per Färg"
)

# Pris per Klarhet
bar_clarity_trace = go.Bar(
    x=avg_price_by_clarity.index,
    y=avg_price_by_clarity.values,
    marker_color='silver',
    name="Pris per Klarhet"
)

# Pris per Slipkvalitet
bar_cut_trace = go.Bar(
    x=avg_price_by_cut_gia.index,
    y=avg_price_by_cut_gia.values,
    marker_color='gold',
    name="Pris per Cut"
)

# Pie: Cut
pie_cut_trace = go.Pie(
    labels=cut_counts.index,
    values=cut_counts.values,
    name="Fördelning Cut",
    hole=0.3
)

# Pie: Clarity
pie_clarity_trace = go.Pie(
    labels=clarity_counts.index,
    values=clarity_counts.values,
    name="Fördelning Clarity",
    hole=0.3
)

# Skapa 2x3 grid
fig_grid = make_subplots(
    rows=2, cols=3,
    subplot_titles=[
        "Pris vs Vikt (Carat)", "Pris per Färg", "Pris per Klarhet",
        "Pris per Slipkvalitet", "Fördelning: Cut", "Fördelning: Clarity"
    ],
    specs=[[{"type": "scatter"}, {"type": "bar"}, {"type": "bar"}],
           [{"type": "bar"}, {"type": "domain"}, {"type": "domain"}]]
)

# Lägg till spår i rätt ruta
fig_grid.add_trace(scatter_trace, row=1, col=1)
fig_grid.add_trace(bar_color_trace, row=1, col=2)
fig_grid.add_trace(bar_clarity_trace, row=1, col=3)
fig_grid.add_trace(bar_cut_trace, row=2, col=1)
fig_grid.add_trace(pie_cut_trace, row=2, col=2)
fig_grid.add_trace(pie_clarity_trace, row=2, col=3)

# Anpassa layout
fig_grid.update_layout(
    height=800, width=1200,
    title_text="Diamantanalys – Visualiseringar i Grid",
    template="plotly_dark",
    showlegend=False
)

fig_grid.show()
