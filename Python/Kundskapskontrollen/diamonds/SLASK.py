import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Läs in och rensa datan
df = pd.read_excel(r'C:\Users\SebbePwnYou\repos\Skola\Python\Kundskapskontrollen\diamonds\diamonds.xlsx')
df_clean = df.dropna()

# Gruppanalyser för stapeldiagram
avg_price_by_color = df_clean.groupby("color")["price"].mean().sort_index()
avg_price_by_clarity = df_clean.groupby("clarity")["price"].mean().sort_index()
avg_price_by_cut = df_clean.groupby("cut")["price"].mean().sort_index()

# Räkna kategorier för pie charts
cut_counts = df_clean["cut"].value_counts()
clarity_counts = df_clean["clarity"].value_counts()

# Diskretisera numeriska variabler i 3 grupper
depth_bins = pd.qcut(df_clean["depth"], q=3, labels=["Låg", "Mellan", "Hög"])
depth_counts = depth_bins.value_counts().sort_index()

table_bins = pd.qcut(df_clean["table"], q=3, labels=["Låg", "Mellan", "Hög"])
table_counts = table_bins.value_counts().sort_index()

carat_bins = pd.qcut(df_clean["carat"], q=3, labels=["Låg", "Mellan", "Hög"])
carat_counts = carat_bins.value_counts().sort_index()

# Skapa subplot-grid: 3 rader x 3 kolumner
fig, axs = plt.subplots(3, 3, figsize=(20, 16))

# 1. Pris vs Carat (scatter)
axs[0, 0].scatter(df_clean["carat"], df_clean["price"], alpha=0.4)
axs[0, 0].set_title("Pris vs Vikt (Carat)")
axs[0, 0].set_xlabel("Carat")
axs[0, 0].set_ylabel("Pris (USD)")

# 2. Genomsnittligt pris per färg
color_map = {
    'D': '#4B9CD3',
    'E': '#76B041',
    'F': '#FFD700',
    'G': '#FF7F50',
    'H': '#D87093',
    'I': '#9370DB',
    'J': '#A9A9A9'
}

bar_colors = [color_map.get(color, 'gray') for color in avg_price_by_color.index]

axs[0, 1].bar(avg_price_by_color.index, avg_price_by_color.values, color=bar_colors)
axs[0, 1].set_title("Pris per Färg")
axs[0, 1].set_xlabel("Färg")
axs[0, 1].set_ylabel("Pris")

# 3. Genomsnittligt pris per klarhet
axs[0, 2].bar(avg_price_by_clarity.index, avg_price_by_clarity.values, color="silver")
axs[0, 2].set_title("Pris per Klarhet")
axs[0, 2].set_xlabel("Klarhet")
axs[0, 2].set_ylabel("Pris")

# 4. Genomsnittligt pris per cut
axs[1, 0].bar(avg_price_by_cut.index, avg_price_by_cut.values, color="green")
axs[1, 0].set_title("Pris per Slipkvalitet (Cut)")
axs[1, 0].set_xlabel("Cut")
axs[1, 0].set_ylabel("Pris")

# 5. Pie chart – Cut
axs[1, 1].pie(cut_counts.values, labels=cut_counts.index, autopct='%1.1f%%', startangle=90)
axs[1, 1].set_title("Fördelning: Cut")
axs[1, 1].axis('equal')

# 6. Pie chart – Clarity
axs[1, 2].pie(clarity_counts.values, labels=clarity_counts.index, autopct='%1.1f%%', startangle=90)
axs[1, 2].set_title("Fördelning: Clarity")
axs[1, 2].axis('equal')

# 7. Pie chart – Depth
axs[2, 0].pie(depth_counts.values, labels=depth_counts.index, autopct='%1.1f%%', startangle=90)
axs[2, 0].set_title("Fördelning: Depth")
axs[2, 0].axis('equal')

# 8. Pie chart – Table
axs[2, 1].pie(table_counts.values, labels=table_counts.index, autopct='%1.1f%%', startangle=90)
axs[2, 1].set_title("Fördelning: Table")
axs[2, 1].axis('equal')

# 9. Pie chart – Carat
axs[2, 2].pie(carat_counts.values, labels=carat_counts.index, autopct='%1.1f%%', startangle=90)
axs[2, 2].set_title("Fördelning: Carat")
axs[2, 2].axis('equal')

plt.tight_layout()
plt.subplots_adjust(hspace=0.4)  # Ökar mellanrummet mellan rader

plt.show()
