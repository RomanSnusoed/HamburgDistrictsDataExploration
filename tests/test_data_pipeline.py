import geopandas as gpd
import pandas as pd

from src.app import load_data
from src.data_loader import load_districts, load_pollution_data, load_traffic_data
from src.preprocessing import (
    aggregate_pollution_by_district,
    normalize_metrics,
    prepare_geospatial_dataset,
)


def test_load_data_returns_expected_columns():
    data = load_data()
    assert isinstance(data, pd.DataFrame)
    required = {"district", "indicator", "year", "value", "normalized_value", "geometry"}
    assert required.issubset(data.columns)
    assert not data.empty


def test_normalize_metrics_range_between_zero_and_one():
    pollution = load_pollution_data()
    aggregated = aggregate_pollution_by_district(pollution)
    normalized = normalize_metrics(aggregated, group_by=["indicator", "year"])
    assert normalized["normalized_value"].between(0, 1).all()


def test_prepare_geospatial_dataset_joins_geometry():
    pollution = load_pollution_data()
    traffic = load_traffic_data()
    districts = load_districts()
    geodata = prepare_geospatial_dataset(pollution, traffic, districts)
    assert isinstance(geodata, gpd.GeoDataFrame)
    assert geodata["geometry"].notna().all()
    assert geodata["indicator"].isin({"NO2", "PM10", "O3", "TRAFFIC"}).all()
