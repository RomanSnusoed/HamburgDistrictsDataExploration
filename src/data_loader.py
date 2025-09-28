"""Utilities for loading UrbanEcoViz source datasets."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import geopandas as gpd
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class DataSourceError(RuntimeError):
    """Raised when one of the bundled datasets fails validation."""


_POLLUTION_COLUMNS: Iterable[str] = {
    "station_id",
    "station_name",
    "district",
    "latitude",
    "longitude",
    "year",
    "pollutant",
    "value",
}

_TRAFFIC_COLUMNS: Iterable[str] = {
    "district",
    "year",
    "traffic_volume",
}

_DISTRICT_COLUMNS: Iterable[str] = {
    "district",
    "geometry",
}


def _validate_columns(frame: pd.DataFrame, required: Iterable[str], dataset: str) -> None:
    missing = set(required) - set(frame.columns)
    if missing:
        raise DataSourceError(f"{dataset} is missing expected columns: {sorted(missing)}")


def load_pollution_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load Hamburg air-quality readings from the open-data extract."""

    csv_path = Path(path) if path is not None else DATA_DIR / "luftschadstoffe_hamburg.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Pollution dataset not found: {csv_path}")

    pollution = pd.read_csv(csv_path)
    _validate_columns(pollution, _POLLUTION_COLUMNS, "luftschadstoffe_hamburg.csv")

    pollution["pollutant"] = pollution["pollutant"].str.upper()
    pollution["district"] = pollution["district"].str.strip()
    pollution["year"] = pollution["year"].astype(int)
    pollution["value"] = pd.to_numeric(pollution["value"], errors="coerce")
    pollution = pollution.dropna(subset=["latitude", "longitude", "value"])

    return pollution.reset_index(drop=True)


def load_traffic_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load Hamburg road traffic volumes."""

    csv_path = Path(path) if path is not None else DATA_DIR / "verkehrsbelastung_hamburg.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Traffic dataset not found: {csv_path}")

    traffic = pd.read_csv(csv_path)
    _validate_columns(traffic, _TRAFFIC_COLUMNS, "verkehrsbelastung_hamburg.csv")

    traffic["district"] = traffic["district"].str.strip()
    traffic["year"] = traffic["year"].astype(int)
    traffic["traffic_volume"] = pd.to_numeric(traffic["traffic_volume"], errors="coerce")

    return traffic.dropna(subset=["traffic_volume"]).reset_index(drop=True)


def load_districts(path: str | Path | None = None) -> gpd.GeoDataFrame:
    """Load Hamburg district geometries as a GeoDataFrame."""

    geojson_path = Path(path) if path is not None else DATA_DIR / "hamburg_districts.geojson"
    if not geojson_path.exists():
        raise FileNotFoundError(f"District boundaries not found: {geojson_path}")

    districts = gpd.read_file(geojson_path)
    if "district" not in districts.columns:
        raise DataSourceError("District GeoJSON must include a 'district' property")

    districts = districts.rename(columns={"district": "district"})
    districts["district"] = districts["district"].str.strip()
    districts = districts[_DISTRICT_COLUMNS]
    districts = districts.set_crs("EPSG:4326")

    return districts


__all__ = [
    "DATA_DIR",
    "DataSourceError",
    "load_districts",
    "load_pollution_data",
    "load_traffic_data",
]
