import pandas as pd
import numpy as np

# --- Load bilateral imports ---
df = pd.read_csv("processed_imports_full.csv")

# Normalize column names
df = df.rename(columns={
    "reporterISO":"ImporterISO",
    "partnerISO":"ExporterISO",
    "refYear":"Year",
    "primaryValue":"TradeValue"
})
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["TradeValue"] = pd.to_numeric(df["TradeValue"], errors="coerce")

# Use 2028 if present, else latest year
year_target = 2028 if 2028 in df["Year"].unique() else df["Year"].max()
print(f"Using year {year_target} for China export exposure...")

# Get imports from China
imports = (
    df[df["Year"]==year_target]
    .groupby(["ImporterISO","ExporterISO"], as_index=False)["TradeValue"].sum()
)

# Filter China as exporter
china_exports = imports[imports["ExporterISO"]=="CHN"]

# Total imports of each country
total_imports = imports.groupby("ImporterISO", as_index=False)["TradeValue"].sum().rename(columns={"TradeValue":"TotalImports"})

# Merge totals
china_exports = china_exports.merge(total_imports, on="ImporterISO", how="left")
china_exports["ShareFromChina"] = china_exports["TradeValue"] / china_exports["TotalImports"]

# Apply 25% export drop from China
china_exports["ShockValue"] = 0.25 * china_exports["TradeValue"]
china_exports["ShockPct_of_Imports"] = 100 * china_exports["ShockValue"] / china_exports["TotalImports"]

# Sort & display top 5 most exposed
china_exposed = china_exports.sort_values("ShockPct_of_Imports", ascending=False)

print("\n=== Top 5 Countries Most Exposed to China Export Drop (25%) ===")
print(china_exposed[["ImporterISO","TradeValue","TotalImports","ShareFromChina","ShockPct_of_Imports"]].head(5))


