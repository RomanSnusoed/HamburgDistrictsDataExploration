# -*- coding: utf-8 -*-
"""
dtpr.py
-------
Data preparation utilities for harmonizing and merging geographic (GeoDataFrame)
and statistical (DataFrame) information for Hamburg districts.

Main responsibilities:
- Normalize district naming conventions between CSV and OSM data
- Expand grouped district names into individual entries
- Remove irrelevant rows
- Merge cleaned statistics with geographic geometries
"""

import pandas as pd

# -------------------------------------------------------------------
# Normalization mappings
# -------------------------------------------------------------------
# Fixes for inconsistent district naming
NAME_FIXES = {
    "hamburg-altstadt": "altstadt",
    "altstadt": "altstadt",
}

# Grouped district names that should be split into multiple entries
GROUP_MAP = {
    "kleiner grasbrook und steinwerder": ["kleiner grasbrook", "steinwerder"],
    "moorburg und altenwerder": ["moorburg", "altenwerder"],
    "neuland und gut moor": ["neuland", "gut moor"],
    "waltershof und finkenwerder": ["waltershof", "finkenwerder"],
}

# Rows that should be ignored entirely
IGNORE = {"korrigierte fassung vom 04.01.2024"}


# -------------------------------------------------------------------
# Data preparation function
# -------------------------------------------------------------------
def prepare_data(gdf, df):
    """
    Clean and align district naming, handle grouped rows,
    filter out ignored records, and merge statistics with GeoDataFrame.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        Geometries of Hamburg districts (loaded from OSM).
    df : pandas.DataFrame
        Statistical indicators per district (loaded from CSV).

    Returns
    -------
    merged : geopandas.GeoDataFrame
        Combined geospatial dataset with attached statistical columns.
    """
    # --- Normalize district names ---
    df["district"] = df["district"].astype(str).str.strip().str.lower()
    df["district"] = df["district"].apply(lambda x: NAME_FIXES.get(x, x))

    # Remove ignored rows
    df = df[~df["district"].isin(IGNORE)]

    # --- Expand grouped districts ---
    expanded_rows = []
    for _, row in df.iterrows():
        if row["district"] in GROUP_MAP:
            for target in GROUP_MAP[row["district"]]:
                new_row = row.copy()
                new_row["district"] = target
                expanded_rows.append(new_row)
        else:
            expanded_rows.append(row)
    df = pd.DataFrame(expanded_rows)

    # --- Merge with geographic data ---
    stats_set = set(df["district"])
    gdf = gdf[gdf["district"].isin(stats_set)].copy()
    merged = gdf.merge(df, on="district", how="left")

    return merged
