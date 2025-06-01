
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