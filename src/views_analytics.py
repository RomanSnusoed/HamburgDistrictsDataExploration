import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ---------- Top-10 Bar Chart ----------
def show_top10(merged: pd.DataFrame, indicator: str) -> None:
    """
    Display a horizontal bar chart for the Top-10 districts
    by the selected indicator.
    """
    top10 = merged.sort_values(by=indicator, ascending=False).head(10)
    fig = px.bar(
        top10,
        x=indicator,
        y="district",
        orientation="h",
        title=f"🏆 Top 10 Districts by {indicator}",
        text=indicator,
        color=indicator,
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        template="plotly_dark",
        height=500
    )
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)


# ---------- Histogram ----------
def show_distribution(merged: pd.DataFrame, indicator: str) -> None:
    """
    Display a histogram to visualize the distribution of the selected indicator
    across all districts.
    """
    bins = st.slider("📊 Number of bins", 5, 50, 20, key=f"bins_{indicator}")
    fig = px.histogram(
        merged,
        x=indicator,
        nbins=bins,
        title=f"Distribution of {indicator}",
        color_discrete_sequence=["#4e79a7"]
    )
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)


# ---------- Boxplot ----------
def show_boxplot(merged: pd.DataFrame, indicator: str) -> None:
    """
    Display a boxplot with outliers to quickly inspect distribution,
    quartiles, and potential anomalies.
    """
    fig = px.box(
        merged,
        y=indicator,
        points="all",
        title=f"📦 Boxplot — {indicator}",
        color_discrete_sequence=["#e15759"]
    )
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)


# ---------- Scatter Plot (Correlation) ----------
def show_scatter(merged: pd.DataFrame, numeric_cols: list[str]) -> None:
    """
    Display a scatter plot between any two numeric indicators.
    Useful for exploring correlations and relationships.
    """
    st.subheader("📈 Indicator Correlation")
    col1, col2 = st.columns(2)
    x_col = col1.selectbox("Select X-axis indicator", numeric_cols, key="x_scatter")
    y_col = col2.selectbox("Select Y-axis indicator", numeric_cols, key="y_scatter")

    if x_col != y_col:
        fig = px.scatter(
            merged,
            x=x_col,
            y=y_col,
            hover_name="district",
            trendline="ols",
            color_discrete_sequence=["#59a14f"]
        )
        fig.update_layout(
            title=f"📊 {x_col} vs {y_col}",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

