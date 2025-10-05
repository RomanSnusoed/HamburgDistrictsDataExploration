# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# ---------- Top-10 Districts ----------
def show_top10_chart(merged: pd.DataFrame, indicator: str) -> None:
    """
    Display a horizontal bar chart of the Top-10 districts
    based on the selected indicator.
    """
    top10 = merged.sort_values(by=indicator, ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.barh(top10["district"], top10[indicator], color="#4e79a7")
    ax.invert_yaxis()  # Top district on top

    # Add value labels next to bars
    for bar in bars:
        ax.text(
            bar.get_width() + max(top10[indicator]) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{int(bar.get_width()):,}".replace(",", " "),
            va="center"
        )

    ax.set_xlabel(indicator)
    ax.set_title(f"Top 10 Districts — {indicator}", fontsize=14, pad=15)
    plt.tight_layout()
    st.pyplot(fig)


# ---------- District-to-District Comparison ----------
def show_comparison_chart(merged: pd.DataFrame, indicator: str, district_a: str, district_b: str) -> None:
    """
    Compare the indicator values between two selected districts
    using a simple two-bar chart.
    """
    data = merged.set_index("district")
    if district_a not in data.index or district_b not in data.index:
        st.warning("⚠️ One or both selected districts are not present in the dataset.")
        return

    values = [data.loc[district_a, indicator], data.loc[district_b, indicator]]

    fig, ax = plt.subplots(figsize=(6, 6))
    bars = ax.bar([district_a, district_b], values, color=["#59a14f", "#e15759"])

    # Add value labels on top of bars
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.01,
            f"{int(bar.get_height()):,}".replace(",", " "),
            ha="center", va="bottom"
        )

    ax.set_ylabel(indicator)
    ax.set_title(f"Comparison: {district_a} vs {district_b}", fontsize=14, pad=15)
    plt.tight_layout()
    st.pyplot(fig)
