# -*- coding: utf-8 -*-
from __future__ import annotations
import io
import pandas as pd
import streamlit as st
import data_loader
import dtpr

# Streamlit page configuration
st.set_page_config(layout="wide", page_title="Hamburg — Data Table")

st.title("Data Table")

# -----------------------------
# 1) Load and prepare data
# -----------------------------
gdf = data_loader.load_geo()
df  = data_loader.load_stats()
merged = dtpr.prepare_data(gdf, df).drop(columns=["geometry"])

# Identify numeric columns
numeric_cols = [
    c for c in merged.columns
    if c not in ("district",) and merged[c].dtype.kind in "iufc"
]
if not numeric_cols:
    st.error("No numeric columns found.")
    st.stop()

# Indicator from global session state (synced with map / analytics pages)
indicator = st.session_state.get("indicator", numeric_cols[0])

# -----------------------------
# 2) Filters
# -----------------------------
with st.expander("Filters", expanded=True):
    # District selection filter
    districts = merged["district"].sort_values().tolist()
    selected_districts = st.multiselect(
        "Districts",
        options=districts,
        default=[],
        placeholder="Start typing to search..."
    )

    # Numeric range filter for selected indicator
    min_v = float(pd.to_numeric(merged[indicator], errors="coerce").min())
    max_v = float(pd.to_numeric(merged[indicator], errors="coerce").max())
    r = st.slider(
        f"Range for “{indicator}”",
        min_value=min_v,
        max_value=max_v,
        value=(min_v, max_v)
    )

    # Substring search
    query = st.text_input("Search by district name (substring):", "")

# -----------------------------
# 3) Apply filters
# -----------------------------
flt = merged.copy()

# Filter by district selection
if selected_districts:
    flt = flt[flt["district"].isin(selected_districts)]

# Filter by numeric range
flt = flt[
    (pd.to_numeric(flt[indicator], errors="coerce") >= r[0]) &
    (pd.to_numeric(flt[indicator], errors="coerce") <= r[1])
]

# Filter by text search
if query.strip():
    q = query.strip().lower()
    flt = flt[flt["district"].str.contains(q, case=False, na=False)]

# -----------------------------
# 4) KPI metrics for current selection
# -----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Number of districts", f"{len(flt):,}".replace(",", " "))
c2.metric("Total value", f"{pd.to_numeric(flt[indicator], errors='coerce').sum():,.0f}".replace(",", " "))
c3.metric("Average", f"{pd.to_numeric(flt[indicator], errors='coerce').mean():,.2f}".replace(",", " "))
c4.metric("Median", f"{pd.to_numeric(flt[indicator], errors='coerce').median():,.2f}".replace(",", " "))

# -----------------------------
# 5) Data Table
# -----------------------------
st.subheader(f"Indicator Table: {indicator}")
st.dataframe(flt.sort_values(indicator, ascending=False), use_container_width=True)

# -----------------------------
# 6) CSV Export
# -----------------------------
buff = io.StringIO()
flt.to_csv(buff, index=False, encoding="utf-8")
st.download_button(
    "Download filtered CSV",
    buff.getvalue().encode("utf-8"),
    file_name=f"hamburg_{indicator}_filtered.csv",
    mime="text/csv",
)
