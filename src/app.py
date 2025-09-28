"""Streamlit entry-point for UrbanEcoViz."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from .data_loader import load_districts, load_pollution_data, load_traffic_data
from .preprocessing import normalize_metrics, prepare_geospatial_dataset
from .visualization import build_deck, create_pollution_layer, create_traffic_layer


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load and preprocess all metrics for the dashboard."""

    pollution = load_pollution_data()
    traffic = load_traffic_data()
    districts = load_districts()
    geodata = prepare_geospatial_dataset(pollution, traffic, districts)
    return normalize_metrics(geodata, group_by=["indicator", "year"])


def main() -> None:
    st.set_page_config(page_title="UrbanEcoViz", layout="wide")
    st.title("UrbanEcoViz — Hamburg Environmental Intelligence")
    st.markdown(
        """
        Реальные данные из портала Transparenz Hamburg: концентрации NO₂ и PM₁₀ по станциям,
        а также среднегодовая нагрузка на дорожную сеть. Используйте селектор, чтобы сравнить показатели
        между районами в разные годы на интерактивной 3D-карте.
        """
    )

    try:
        dataset = load_data()
    except Exception as exc:  # pragma: no cover - Streamlit surface
        st.error(f"Не удалось загрузить данные: {exc}")
        return

    indicator_options = ["NO2", "PM10", "TRAFFIC"]
    available_years = sorted(dataset["year"].unique())

    with st.sidebar:
        st.header("Фильтры")
        indicator = st.selectbox(
            "Показатель",
            indicator_options,
            format_func=lambda value: {"NO2": "NO₂", "PM10": "PM₁₀", "TRAFFIC": "Traffic"}.get(value, value),
        )
        year = st.slider("Год", min_value=int(min(available_years)), max_value=int(max(available_years)), value=int(max(available_years)))
        st.caption("Источник: https://suche.transparenz.hamburg.de")

    filtered = dataset[(dataset["indicator"] == indicator.upper()) & (dataset["year"] == year)]
    if filtered.empty:
        st.warning("Нет данных для выбранной комбинации фильтров.")
        return

    if indicator.upper() == "TRAFFIC":
        layer = create_traffic_layer(filtered)
    else:
        layer = create_pollution_layer(filtered, indicator)

    deck = build_deck([layer])
    st.pydeck_chart(deck)

    st.subheader("Таблица показателей")
    display = filtered[["district", "indicator", "year", "value", "normalized_value"]].copy()
    display["indicator"] = display["indicator"].replace({"TRAFFIC": "Traffic"})
    st.dataframe(display.rename(columns={"district": "District", "value": "Value", "normalized_value": "Normalized"}), use_container_width=True)

    st.caption("""Данные нормализованы в диапазоне 0–1 по показателю и году для корректного сравнения высоты колонн.""")


if __name__ == "__main__":
    main()
