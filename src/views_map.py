import folium
from streamlit_folium import st_folium

def show_map(gdf, merged, indicator: str) -> None:
    """
    Display an interactive choropleth map of Hamburg districts using Folium.
    The map colors districts by the selected numeric indicator.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        GeoDataFrame containing district geometries.
    merged : pandas.DataFrame
        Merged dataset of district geometries and statistics.
    indicator : str
        Name of the numeric column to visualize on the map.
    """

    # Initialize the map (slightly zoomed in by default for better view)
    m = folium.Map(
        location=[53.55, 10.0],
        zoom_start=10.7,        # slightly closer view for better framing
        min_zoom=9,
        max_zoom=14,
        tiles="CartoDB dark_matter",
        scrollWheelZoom=False
    )

    # Add a choropleth layer to color districts by indicator values
    folium.Choropleth(
        geo_data=gdf,
        data=merged[["district", indicator]],
        columns=["district", indicator],
        key_on="feature.properties.district",
        fill_color="Blues",          # 🌈 clearer and more contrasting palette
        bins=14,                     # finer color gradation than default
        nan_fill_color="#2f2f2f",    # neutral color for missing data
        fill_opacity=0.85,
        line_opacity=0.3,
        legend_name=indicator,
    ).add_to(m)

    # Add district tooltips (name + indicator value)
    folium.GeoJson(
        merged[["district", "geometry", indicator]],
        name="labels",
        style_function=lambda x: {"fillOpacity": 0, "color": "#00000000"},
        tooltip=folium.GeoJsonTooltip(
            fields=["district", indicator],
            aliases=["District", indicator],
            localize=True,
        ),
    ).add_to(m)

    # Render the map inside Streamlit
    st_folium(m, width=1200, height=750)
