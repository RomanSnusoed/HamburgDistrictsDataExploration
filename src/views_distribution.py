import streamlit as st
import matplotlib.pyplot as plt

def show_distribution(merged, indicator: str) -> None:
    """
    Display a simple histogram using Matplotlib to show the distribution
    of a selected indicator across all districts.

    Parameters
    ----------
    merged : pandas.DataFrame
        Merged dataset containing district statistics.
    indicator : str
        Name of the numeric column to visualize.
    """
    # Prepare the data (drop NaNs just in case)
    values = merged[indicator].dropna()

    # Create the histogram figure
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(values, bins=20, color="#4e79a7", edgecolor="white")

    # Set English titles and labels
    ax.set_title(f"Distribution of {indicator}", fontsize=13)
    ax.set_xlabel(indicator, fontsize=11)
    ax.set_ylabel("Number of districts", fontsize=11)

    # Clean up the grid
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Render in Streamlit
    st.pyplot(fig)
