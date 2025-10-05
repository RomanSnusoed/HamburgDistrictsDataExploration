# -*- coding: utf-8 -*-
from __future__ import annotations
import streamlit as st
import data_loader
import dtpr
import views_map

# -------------------------------------------
# Streamlit Page Configuration
# -------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="Hamburg Districts — with Statistics"
)

st.title("Hamburg Districts — with Statistics")

# -------------------------------------------
# 1) Load & prepare data
# (Caching is handled inside data_loader if needed)
# -------------------------------------------
gdf = data_loader.load_geo()
df  = data_loader.load_stats()
merged = dtpr.prepare_data(gdf, df)

# Identify numeric columns (excluding geometry + district names)
numeric_cols = [
    c for c in merged.columns
    if c not in ("district", "geometry") and merged[c].dtype.kind in "iufc"
]
if not numeric_cols:
    st.error("No numeric columns found. Check your CSV file.")
    st.stop()

# -------------------------------------------
# 2) Global indicator selection
# (Stored in st.session_state so it's shared across pages)
# -------------------------------------------
if "indicator" not in st.session_state:
    st.session_state["indicator"] = numeric_cols[0]

st.sidebar.header("Settings")
indicator = st.sidebar.selectbox(
    "Select indicator:",
    numeric_cols,
    index=numeric_cols.index(st.session_state["indicator"]) 
          if st.session_state["indicator"] in numeric_cols else 0,
)
st.session_state["indicator"] = indicator  # make selection globally available

# -------------------------------------------
# 3) Map visualization
# -------------------------------------------
views_map.show_map(gdf, merged, indicator)

# -------------------------------------------
# 4) Footer / user tip
# -------------------------------------------
st.caption(
    "💡 Tip: Use the sidebar to switch indicators. "
    "Additional visualizations are available in the “Table” and “Analytics” tabs in the top navigation."
)
