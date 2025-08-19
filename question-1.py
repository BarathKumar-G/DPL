import pandas as pd
import numpy as np

# --- Load imports dataset ---
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

latest_year = df["Year"].max()

# Reconstruct exports (Exporter -> Importer)
exports = (
    df[df["Year"]==latest_year]
    .groupby(["ExporterISO","ImporterISO"], as_index=False)["TradeValue"].sum()
    .rename(columns={"TradeValue":"Exports"})
)

# Total exports per exporter
totals = exports.groupby("ExporterISO", as_index=False)["Exports"].sum().rename(columns={"Exports":"TotalExports"})

# Merge totals back
exports = exports.merge(totals, on="ExporterISO", how="left")
exports["Share"] = exports["Exports"] / exports["TotalExports"]

# Pick the top partner row for each exporter
idx = exports.groupby("ExporterISO")["Share"].idxmax()
top_partner = exports.loc[idx].reset_index(drop=True)

# Rename + compute dependency
top_partner = top_partner.rename(columns={
    "ImporterISO":"TopPartnerISO",
    "Exports":"TopPartnerExports",
    "Share":"TDI"
})

# Simulate 40% collapse in 2026
top_partner["ExportShockValue"] = 0.40 * top_partner["TopPartnerExports"]
top_partner["Shock_asPct_of_TotalExports"] = 100 * top_partner["ExportShockValue"] / top_partner["TotalExports"]

# Print results
print("\n=== Trade Dependency Index (all countries) ===")
print(top_partner[["ExporterISO","TopPartnerISO","TDI","Shock_asPct_of_TotalExports"]].sort_values("TDI", ascending=False).head(10))

print("\n=== Top 3 Vulnerable Countries ===")
print(top_partner.sort_values("TDI", ascending=False).head(3))
