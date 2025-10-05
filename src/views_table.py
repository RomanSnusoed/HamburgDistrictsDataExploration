import streamlit as st
import pandas as pd

def show_table(merged: pd.DataFrame, indicator: str) -> pd.DataFrame:
    """
    Display a filtered and styled data table for a selected numeric indicator.

    Parameters
    ----------
    merged : pandas.DataFrame
        Dataset containing district statistics (already merged with geometry).
    indicator : str
        Name of the numeric column to display and filter.

    Returns
    -------
    pandas.DataFrame
        The filtered DataFrame currently displayed in the table.
    """
    st.subheader(f"📋 Data Table — {indicator}")

    # --- 1. Range filter ---
    # Allow users to filter districts by the selected indicator's value range
    min_val = float(merged[indicator].min())
    max_val = float(merged[indicator].max())
    selected_min, selected_max = st.slider(
        "Select value range",
        min_val,
        max_val,
        (min_val, max_val),
        step=(max_val - min_val) / 100
    )

    filtered = merged[(merged[indicator] >= selected_min) & (merged[indicator] <= selected_max)]

    # --- 2. Sorting ---
    # Sort the table in descending order for better ranking visibility
    df_sorted = filtered.sort_values(by=indicator, ascending=False).reset_index(drop=True)

    # --- 3. Heatmap-style cell highlighting ---
    # Apply a gradient background to the indicator column for visual emphasis
    styled = (
        df_sorted.style
        .background_gradient(subset=[indicator], cmap="Blues")
        .format(precision=2)
    )

    st.dataframe(styled, use_container_width=True)

    # --- 4. CSV export ---
    # Provide a download button to export the filtered table
    csv = df_sorted.to_csv(index=False).encode("utf-8")
    st.download_button(
        "💾 Download CSV",
        csv,
        f"{indicator}_filtered.csv",
        "text/csv",
        key="download-csv"
    )

    return filtered
