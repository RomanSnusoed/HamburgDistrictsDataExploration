# -*- coding: utf-8 -*-
"""
views_charts.py
---------------
A collection of reusable Plotly-based visualization functions
for exploring Hamburg district statistics.

Charts included:
- Top-10 horizontal bar chart
- Histogram (distribution)
- Boxplot (outlier detection)
- Scatter plot with trendline (OLS)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# -------------------------------------------------------------------
# 1) Top-10 bar chart
# -------------------------------------------------------------------
def show_top10(merged, indicator: str) -> None:
    """
    Display the Top-10 districts by the selected indicator.

    Parameters
    ----------
    merged : pandas.DataFrame
        Merged dataset with numerical indicators per district.
    indicator : str
        Name of the indicator column to visualize.
    """
    top10 = merged.sort_values(by=indicator, ascending=False).head(10)
    fig = px.bar(
        top10,
        x=indicator,
        y="district",
        orientation="h",
        title=f"🏆 Top-10 districts by: {indicator}",
        text=indicator,
        color=indicator,
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        template="plotly_dark",
        height=500,
    )
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------
# 2) Histogram
# -------------------------------------------------------------------
def show_distribution(merged, indicator: str) -> None:
    """
    Show histogram of indicator values across all districts.

    Allows adjusting the number of bins interactively.
    """
    bins = st.slider(
        "📊 Number of bins",
        5, 50, 20,
        key=f"bins_{indicator}"
    )
    fig = px.histogram(
        merged,
        x=indicator,
        nbins=bins,
        title=f"Distribution of {indicator}",
        color_discrete_sequence=["#4e79a7"],
    )
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------
# 3) Boxplot
# -------------------------------------------------------------------
def show_boxplot(merged, indicator: str) -> None:
    """
    Display a boxplot to detect outliers and visualize data spread.
    """
    fig = px.box(
        merged,
        y=indicator,
        points="all",
        title=f"📦 Boxplot for: {indicator}",
        color_discrete_sequence=["#e15759"],
    )
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------
# 4) Scatter plot with trendline
# -------------------------------------------------------------------
def show_scatter(merged, numeric_cols: list[str]) -> None:
    """
    Interactive scatter plot for comparing two numerical indicators.

    Includes a linear regression trendline (OLS) for quick insight.
    """
    st.subheader("📈 Compare two indicators")

    col1, col2 = st.columns(2)
    x_col = col1.selectbox("X-axis indicator", numeric_cols, key="x_scatter")
    y_col = col2.selectbox("Y-axis indicator", numeric_cols, key="y_scatter")

    if x_col != y_col:
        fig = px.scatter(
            merged,
            x=x_col,
            y=y_col,
            hover_name="district",
            trendline="ols",
            color_discrete_sequence=["#59a14f"],
        )
        fig.update_layout(
            title=f"📊 Relationship: {x_col} vs {y_col}",
            template="plotly_dark",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)
