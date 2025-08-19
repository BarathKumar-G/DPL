import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import math

# ====== Load dataset ======
df = pd.read_csv("processed_imports_full.csv")

# ====== Identify columns ======
def find_col(candidates):
    for c in df.columns:
        if any(c.lower().startswith(x.lower()) or x.lower() in c.lower() for x in candidates):
            return c
    return None

importer_col = find_col(["reporteriso","reporter","importer"])
exporter_col = find_col(["partneriso","partner","exporter"])
year_col     = find_col(["refyear","year"])
value_col    = find_col(["primaryvalue","tradevalue","value"])

df["ImporterISO"] = df[importer_col].astype(str).str.upper().str.strip()
df["ExporterISO"] = df[exporter_col].astype(str).str.upper().str.strip()
df["Year"]        = pd.to_numeric(df[year_col], errors="coerce")
df["TradeValue"]  = pd.to_numeric(df[value_col], errors="coerce")

df = df.dropna(subset=["ImporterISO","ExporterISO","Year","TradeValue"])

# ====== Use latest year ======
latest = int(df["Year"].max())
df_latest = df[df["Year"] == latest].copy()

# ====== Aggregate exports ======
exports = (
    df_latest.groupby(["ExporterISO","ImporterISO"], as_index=False)["TradeValue"]
    .sum()
    .rename(columns={"TradeValue":"Exports"})
)

# ====== Totals per country ======
exports_sum = exports.groupby("ExporterISO", as_index=False)["Exports"].sum()
exports_sum = exports_sum.rename(columns={"ExporterISO":"ISO","Exports":"ExportsTotal"})

imports_sum = exports.groupby("ImporterISO", as_index=False)["Exports"].sum()
imports_sum = imports_sum.rename(columns={"ImporterISO":"ISO","Exports":"ImportsTotal"})

trade_sum = exports_sum.merge(imports_sum, on="ISO", how="outer").fillna(0)
trade_sum["TotalTrade"] = trade_sum["ExportsTotal"] + trade_sum["ImportsTotal"]

# ====== Pick top 25 ======
top25 = trade_sum.sort_values("TotalTrade", ascending=False).head(25)
top25_list = set(top25["ISO"].tolist())

edges = exports[
    (exports["ExporterISO"].isin(top25_list)) &
    (exports["ImporterISO"].isin(top25_list))
].copy()

# ====== Build graph ======
G = nx.DiGraph()
for _, r in edges.iterrows():
    if r["Exports"] > 0:
        G.add_edge(r["ExporterISO"], r["ImporterISO"], weight=float(r["Exports"]))

for iso in top25_list:
    if iso not in G:
        G.add_node(iso)

# ====== Centrality ======
bet = nx.betweenness_centrality(G, weight="weight", normalized=True)
deg_tot = {n: G.degree(n, weight="weight") for n in G.nodes()}
centrality_df = pd.DataFrame([
    {"ISO":n, "Betweenness":bet.get(n,0), "DegTotal":deg_tot.get(n,0)}
    for n in G.nodes()
]).sort_values("Betweenness", ascending=False)

print("\nTop 5 most central countries (by betweenness):")
print(centrality_df.head(5))

# ====== Remove most central ======
most_central = centrality_df.iloc[0]["ISO"]
G_removed = G.copy()
G_removed.remove_node(most_central)

# ====== Plotting ======
plt.figure(figsize=(18,9))
pos = nx.spring_layout(G, seed=42, k=0.5)

# Node size by trade, color by centrality
sizes = [trade_sum.set_index("ISO").loc[n,"TotalTrade"]/1e9 if n in trade_sum["ISO"].values else 200 
         for n in G.nodes()]
colors = [bet.get(n,0) for n in G.nodes()]

# BEFORE
plt.subplot(1,2,1)
nx.draw_networkx_edges(G, pos, alpha=0.2, arrowsize=6, width=0.5)
nodes = nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors, cmap="viridis")
labels = {n:n for n in centrality_df.head(10)["ISO"]}  # label top 10 only
nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_weight="bold")
plt.title(f"Trade Network (Top 25) - {latest}\nBefore Removal", fontsize=14, fontweight="bold")
plt.colorbar(nodes, shrink=0.7, label="Betweenness Centrality")

# AFTER
plt.subplot(1,2,2)
nx.draw_networkx_edges(G_removed, pos, alpha=0.2, arrowsize=6, width=0.5)
sizes2 = [sizes[i] for i,n in enumerate(G.nodes()) if n!=most_central]
colors2 = [colors[i] for i,n in enumerate(G.nodes()) if n!=most_central]
nodes2 = nx.draw_networkx_nodes(G_removed, pos, node_size=sizes2, node_color=colors2, cmap="viridis")
labels2 = {n:n for n in centrality_df.head(10)["ISO"] if n!=most_central}
nx.draw_networkx_labels(G_removed, pos, labels=labels2, font_size=9, font_weight="bold")
plt.title(f"After Removing {most_central}", fontsize=14, fontweight="bold")
plt.colorbar(nodes2, shrink=0.7, label="Betweenness Centrality")

plt.tight_layout()
plt.show()