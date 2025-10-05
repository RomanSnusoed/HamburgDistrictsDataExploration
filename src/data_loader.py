# -*- coding: utf-8 -*-
"""
data_loader.py
--------------
Utility functions for loading geographic and statistical datasets for Hamburg districts.
- Geographic data is retrieved from OpenStreetMap via OSMnx.
- Statistical data is loaded from a preprocessed CSV file in the /data directory.
"""

import pandas as pd
import geopandas as gpd
import osmnx as ox
from pathlib import Path
import streamlit as st

# -------------------------------------------------------------------
# File paths
# -------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATS_READY = DATA_DIR / "2022_ready.csv"


# -------------------------------------------------------------------
# 1) Load district geometries from OpenStreetMap
# -------------------------------------------------------------------
def load_geo() -> gpd.GeoDataFrame:
    """
    Fetch administrative district boundaries for Hamburg from OpenStreetMap
    and return as a cleaned GeoDataFrame.
    """
    districts = ox.features_from_place(
        "Hamburg, Germany",
        tags={"boundary": "administrative"},
    )

    # Keep only polygon geometries (exclude points/lines)
    districts = districts[districts.geometry.type.isin(["Polygon", "MultiPolygon"])]

    # Keep only lowest-level administrative boundaries (admin_level=10)
    if "admin_level" in districts.columns:
        districts = districts[districts["admin_level"] == "10"]

    # Normalize district names
    gdf = districts[["name", "geometry"]].rename(columns={"name": "district"})
    gdf["district"] = (
        gdf["district"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.lower()
    )
    return gdf


# -------------------------------------------------------------------
# 2) Load statistical CSV dataset
# -------------------------------------------------------------------
def load_stats() -> pd.DataFrame:
    """
    Load statistical indicators from '2022_ready.csv'.
    Supports both comma and semicolon delimiters.
    Converts numeric columns to float.
    """
    if not STATS_READY.exists():
        st.error("❌ '2022_ready.csv' not found in /data directory.")
        st.stop()

    # Try comma first, then semicolon as a fallback
    try:
        df = pd.read_csv(STATS_READY, sep=",", encoding="utf-8", engine="python")
    except Exception:
        df = pd.read_csv(STATS_READY, sep=";", encoding="utf-8", engine="python")

    # Clean up column names
    df.columns = [c.strip() for c in df.columns]

    # Ensure 'district' column is present
    if "district" not in df.columns:
        st.error(f"❌ 'district' column not found in CSV. Columns present: {df.columns}")
        st.stop()

    # Convert numeric columns to float
    for col in df.columns:
        if col != "district":
            df[col] = pd.to_numeric(
                df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.replace(" ", "", regex=False),
                errors="coerce"
            )

    return df

