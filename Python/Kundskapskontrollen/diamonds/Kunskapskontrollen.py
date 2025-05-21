# Re-import libraries and reload the dataset after code execution state reset
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the Excel file again
df = pd.read_excel(r'C:\Users\SebbePwnYou\repos\Skola\Python\Kundskapskontrollen\diamonds\diamonds.xlsx')


# Clean the dataset by dropping rows with missing values
df_clean = df.dropna()

# 1. Grouped analysis: Average price by color
avg_price_by_color = df_clean.groupby("color")["price"].mean().sort_index()

# 2. Grouped analysis: Average price by clarity
avg_price_by_clarity = df_clean.groupby("clarity")["price"].mean().sort_index()

# 3. Grouped analysis: Average price by cut
avg_price_by_cut = df_clean.groupby("cut")["price"].mean().sort_index()

# Create visualizations using only Matplotlib
fig, axs = plt.subplots(2, 2, figsize=(16, 12))

# Price vs Carat (scatter)
axs[0, 0].scatter(df_clean["carat"], df_clean["price"], alpha=0.4)
axs[0, 0].set_title("Pris vs Vikt (Carat)")
axs[0, 0].set_xlabel("Carat")
axs[0, 0].set_ylabel("Pris (USD)")

# Price by Color (bar)
axs[0, 1].bar(avg_price_by_color.index, avg_price_by_color.values, color="gold")
axs[0, 1].set_title("Genomsnittligt Pris per Färg")
axs[0, 1].set_xlabel("Färg")
axs[0, 1].set_ylabel("Pris (USD)")

# Price by Clarity (bar)
axs[1, 0].bar(avg_price_by_clarity.index, avg_price_by_clarity.values, color="silver")
axs[1, 0].set_title("Genomsnittligt Pris per Klarhet")
axs[1, 0].set_xlabel("Klarhet")
axs[1, 0].set_ylabel("Pris (USD)")

# Price by Cut (bar)
axs[1, 1].bar(avg_price_by_cut.index, avg_price_by_cut.values, color="green")
axs[1, 1].set_title("Genomsnittligt Pris per Slipkvalitet (Cut)")
axs[1, 1].set_xlabel("Slipkvalitet")
axs[1, 1].set_ylabel("Pris (USD)")

plt.tight_layout()
plt.show()
