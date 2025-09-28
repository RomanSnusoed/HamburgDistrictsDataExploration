"""Pydeck visualization helpers for UrbanEcoViz."""
from __future__ import annotations

from typing import Iterable

import pandas as pd
import pydeck as pdk


_COLOR_MAP = {
    "NO2": (239, 71, 111),
    "PM10": (255, 176, 0),
    "O3": (17, 138, 178),
    "TRAFFIC": (94, 79, 162),
    "POPULATION": (38, 173, 36),
}


def _build_column_layer(data: pd.DataFrame, color: Iterable[int], *, elevation_scale: int = 5000) -> pdk.Layer:
    return pdk.Layer(
        "ColumnLayer",
        data=data,
        get_position="[longitude, latitude]",
        get_elevation="normalized_value * elevation_scale",
        elevation_scale=1,
        radius=200,
        get_fill_color=list(color),
        pickable=True,
        auto_highlight=True,
    )


def create_pollution_layer(data: pd.DataFrame, pollutant: str) -> pdk.Layer:
    """Create a pydeck layer for the requested pollutant."""

    pollutant = pollutant.upper()
    subset = data[data["indicator"] == pollutant]
    if subset.empty:
        raise ValueError(f"No data available for pollutant '{pollutant}'")
    color = _COLOR_MAP.get(pollutant, (100, 100, 100))
    return _build_column_layer(subset, color)


def create_traffic_layer(data: pd.DataFrame) -> pdk.Layer:
    """Create a pydeck layer visualising district traffic volumes."""

    subset = data[data["indicator"] == "TRAFFIC"]
    if subset.empty:
        raise ValueError("Traffic dataset is empty")
    return _build_column_layer(subset, _COLOR_MAP["TRAFFIC"], elevation_scale=0.15)


def create_population_layer(data: pd.DataFrame) -> pdk.Layer:
    """Create a pydeck layer for district population (optional future data)."""

    subset = data[data["indicator"] == "POPULATION"]
    if subset.empty:
        raise ValueError("Population dataset is empty")
    return _build_column_layer(subset, _COLOR_MAP["POPULATION"], elevation_scale=0.2)


def build_deck(layers: Iterable[pdk.Layer]) -> pdk.Deck:
    """Assemble a Deck.gl map with shared view state and tooltip."""

    view_state = pdk.ViewState(latitude=53.5511, longitude=9.9937, zoom=11, pitch=45, bearing=0)
    tooltip = {
        "html": (
            "<b>District:</b> {district}<br/>"
            "<b>Indicator:</b> {indicator}<br/>"
            "<b>Year:</b> {year}<br/>"
            "<b>Value:</b> {value:.1f}<br/>"
            "<b>Normalized:</b> {normalized_value:.2f}"
        ),
        "style": {"backgroundColor": "#1f2937", "color": "#f9fafb"},
    }
    return pdk.Deck(layers=list(layers), initial_view_state=view_state, tooltip=tooltip)


__all__ = [
    "build_deck",
    "create_pollution_layer",
    "create_population_layer",
    "create_traffic_layer",
]
