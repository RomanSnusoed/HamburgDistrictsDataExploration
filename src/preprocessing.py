"""Data preprocessing pipeline for UrbanEcoViz."""
from __future__ import annotations

from typing import Iterable, Sequence

import geopandas as gpd
import pandas as pd


def normalize_metrics(
    frame: pd.DataFrame,
    *,
    value_column: str = "value",
    group_by: Sequence[str] | None = None,
    normalized_column: str = "normalized_value",
) -> pd.DataFrame:
    """Scale metric values to the 0-1 range per group."""

    if value_column not in frame.columns:
        raise KeyError(f"Missing '{value_column}' column for normalization")

    def _scale(series: pd.Series) -> pd.Series:
        min_val = series.min()
        max_val = series.max()
        if pd.isna(min_val) or pd.isna(max_val):
            return pd.Series([pd.NA] * len(series), index=series.index, dtype="float64")
        if max_val == min_val:
            return pd.Series([1.0] * len(series), index=series.index, dtype="float64")
        return (series - min_val) / (max_val - min_val)

    normalized = frame.copy()
    if group_by:
        normalized[normalized_column] = (
            normalized.groupby(list(group_by))[value_column].transform(_scale)
        )
    else:
        normalized[normalized_column] = _scale(normalized[value_column])
    normalized[normalized_column] = normalized[normalized_column].astype(float)
    return normalized


def aggregate_pollution_by_district(pollution: pd.DataFrame) -> pd.DataFrame:
    """Average pollutant concentrations per district and year."""

    required: Iterable[str] = {"district", "year", "pollutant", "value"}
    missing = set(required) - set(pollution.columns)
    if missing:
        raise KeyError(f"Pollution data missing columns: {sorted(missing)}")

    aggregated = (
        pollution.groupby(["district", "year", "pollutant"], dropna=False)["value"]
        .mean()
        .reset_index()
        .rename(columns={"pollutant": "indicator"})
    )
    return aggregated


def prepare_geospatial_dataset(
    pollution: pd.DataFrame,
    traffic: pd.DataFrame,
    districts: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Combine pollution and traffic metrics with district geometries."""

    traffic_required: Iterable[str] = {"district", "year", "traffic_volume"}
    missing_traffic = set(traffic_required) - set(traffic.columns)
    if missing_traffic:
        raise KeyError(f"Traffic data missing columns: {sorted(missing_traffic)}")

    districts_required: Iterable[str] = {"district", "geometry"}
    if not districts_required.issubset(districts.columns):
        raise KeyError("District GeoDataFrame must include 'district' and 'geometry'")

    pollution_long = aggregate_pollution_by_district(pollution)

    traffic_long = traffic.rename(
        columns={"traffic_volume": "value"}
    ).assign(indicator="TRAFFIC")

    metrics = pd.concat([pollution_long, traffic_long], ignore_index=True, sort=False)
    merged = metrics.merge(districts, on="district", how="left")
    missing_geometry = merged["geometry"].isna().sum()
    if missing_geometry:
        raise KeyError(f"Missing district geometry for {missing_geometry} records")

    geoframe = gpd.GeoDataFrame(merged, geometry="geometry", crs=districts.crs)
    centroids = geoframe.geometry.centroid
    geoframe["latitude"] = centroids.y
    geoframe["longitude"] = centroids.x

    return geoframe


__all__ = [
    "aggregate_pollution_by_district",
    "normalize_metrics",
    "prepare_geospatial_dataset",
]
