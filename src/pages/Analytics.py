# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
import streamlit as st
import altair as alt
import data_loader
import dtpr

# Streamlit page setup
st.set_page_config(layout="wide", page_title="Hamburg — Analytics")

st.title("Analytics Dashboard")

# -----------------------------
# 1) Load and prepare data
# -----------------------------
gdf = data_loader.load_geo()
df  = data_loader.load_stats()
# Drop geometry column (not needed for charts)
merged = dtpr.prepare_data(gdf, df).drop(columns=["geometry"])

# Identify numeric columns available for visualization
numeric_cols = [
    c for c in merged.columns
    if c not in ("district",) and merged[c].dtype.kind in "iufc"
]
if not numeric_cols:
    st.error("No numeric columns found in dataset.")
    st.stop()

# Current indicator (selected earlier in session or default to first)
indicator = st.session_state.get("indicator", numeric_cols[0])

# -----------------------------
# 2) KPI metrics (summary stats)
# -----------------------------
mnum = pd.to_numeric(merged[indicator], errors="coerce")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total",   f"{mnum.sum():,.0f}".replace(",", " "))
c2.metric("Average", f"{mnum.mean():,.2f}".replace(",", " "))
c3.metric("Max",     f"{mnum.max():,.0f}".replace(",", " "))
c4.metric("Min",     f"{mnum.min():,.0f}".replace(",", " "))

st.divider()

# -----------------------------
# 3) Top/Bottom districts
# -----------------------------
top_n = st.slider("Number of districts to display in Top/Bottom:", 5, 20, 10)
top_df = merged.nlargest(top_n, indicator)[["district", indicator]]
bot_df = merged.nsmallest(top_n, indicator)[["district", indicator]]

colA, colB = st.columns(2)

with colA:
    st.subheader(f"Top {top_n} districts by «{indicator}»")
    chart_top = alt.Chart(top_df).mark_bar().encode(
        x=alt.X(indicator, title=indicator),
        y=alt.Y("district", sort="-x", title=""),
        tooltip=["district", indicator]
    ).properties(height=400)
    st.altair_chart(chart_top, use_container_width=True)

with colB:
    st.subheader(f"Bottom {top_n} districts by «{indicator}»")
    chart_bot = alt.Chart(bot_df).mark_bar().encode(
        x=alt.X(indicator, title=indicator),
        y=alt.Y("district", sort="x", title=""),
        tooltip=["district", indicator]
    ).properties(height=400)
    st.altair_chart(chart_bot, use_container_width=True)

st.divider()

# -----------------------------
# 4) Distribution (Histogram + Quartiles)
# -----------------------------
st.subheader("Distribution of values across districts")
hist = alt.Chart(merged).mark_bar().encode(
    x=alt.X(f"{indicator}:Q", bin=alt.Bin(maxbins=30), title=indicator),
    y=alt.Y("count()", title="Number of districts"),
    tooltip=[indicator]
).properties(height=300)
st.altair_chart(hist, use_container_width=True)

q1, q2, q3 = mnum.quantile([0.25, 0.5, 0.75])
st.caption(f"Quartiles: Q1={q1:.2f} | Median={q2:.2f} | Q3={q3:.2f}")

st.divider()

# -----------------------------
# 5) Scatterplot: Indicator vs. Population / Density / Area
# -----------------------------
st.subheader("Correlation with other variables")
x_axis = st.selectbox("Select X-axis:", ["Bevölkerung", "Bevölkerungs-dichte", "Fläche in km²"])
scatter = alt.Chart(merged).mark_circle(size=90, opacity=0.7).encode(
    x=alt.X(x_axis, title=x_axis),
    y=alt.Y(indicator, title=indicator),
    tooltip=["district", x_axis, indicator]
).interactive().properties(height=420)
st.altair_chart(scatter, use_container_width=True)

