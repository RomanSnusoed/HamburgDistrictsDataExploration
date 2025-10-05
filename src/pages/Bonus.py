# -*- coding: utf-8 -*-
from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import data_loader
import dtpr

st.set_page_config(layout="wide", page_title="Hamburg — Bonus Insights")
st.title("Бонус-аналитика")

# Данные
gdf = data_loader.load_geo()
df  = data_loader.load_stats()
merged = dtpr.prepare_data(gdf, df).drop(columns=["geometry"])

numeric_cols = [
    c for c in merged.columns
    if c not in ("district",) and merged[c].dtype.kind in "iufc"
]
if not numeric_cols:
    st.error("Нет числовых колонок.")
    st.stop()

indicator = st.session_state.get("indicator", numeric_cols[0])

# --- 1) Сравнение района(ов) со средним по городу ---
st.subheader("Сравнение со средним по городу")

sel_districts = st.multiselect(
    "Выбери 1–3 района:",
    options=merged["district"].sort_values().tolist(),
    default=merged["district"].sample(min(2, len(merged)), random_state=1).tolist()
)

if sel_districts:
    city_avg = float(pd.to_numeric(merged[indicator], errors="coerce").mean())
    comp = pd.DataFrame({
        "entity": sel_districts + ["город (среднее)"],
        indicator: list(pd.to_numeric(merged.set_index("district").loc[sel_districts, indicator], errors="coerce")) + [city_avg]
    })
    bar = alt.Chart(comp).mark_bar().encode(
        x=alt.X(indicator, title=indicator),
        y=alt.Y("entity", sort="-x", title=""),
        tooltip=["entity", indicator],
        color=alt.condition(alt.datum.entity == "город (среднее)",
                            alt.value("#7c3aed"),  # фиолетовый для города
                            alt.value("#2563eb"))   # синий для районов
    ).properties(height=300)
    st.altair_chart(bar, use_container_width=True)

st.divider()

# --- 2) Кластеризация районов по выбранным признакам ---
st.subheader("Кластеризация районов (KMeans)")

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    sklearn_ok = True
except Exception:
    sklearn_ok = False

if not sklearn_ok:
    st.info("Для кластеризации установи зависимость: `pip install scikit-learn`")
else:
    features = st.multiselect(
        "Выбери 2–6 признаков для кластеризации:",
        options=numeric_cols,
        default=[c for c in ["Bevölkerung", "Bevölkerungs-dichte", "Fläche in km²"] if c in numeric_cols]
    )

    k = st.slider("Число кластеров (K):", 2, 8, 4)

    if len(features) >= 2:
        X = merged[features].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy()
        Xs = StandardScaler().fit_transform(X)
        km = KMeans(n_clusters=k, n_init="auto", random_state=17)
        labels = km.fit_predict(Xs)

        view = merged[["district"] + features].copy()
        view["cluster"] = labels
        st.dataframe(view.sort_values("cluster"), use_container_width=True)

        st.caption("Подсказка: кластеры — группы районов с похожим ‘профилем’ по выбранным признакам.")

        # 2D проекция для быстого взгляда (через две первые фичи)
        if len(features) >= 2:
            two = features[:2]
            scatter = alt.Chart(view).mark_circle(size=90, opacity=0.8).encode(
                x=alt.X(two[0], title=two[0]),
                y=alt.Y(two[1], title=two[1]),
                color=alt.Color("cluster:N", legend=alt.Legend(title="Кластер")),
                tooltip=["district", "cluster"] + two
            ).interactive().properties(height=420)
            st.altair_chart(scatter, use_container_width=True)

st.divider()

# --- 3) Профили районов (нормированные значения) ---
st.subheader("Профили выбранных районов (нормированные)")

profile_cols = st.multiselect(
    "Признаки для профиля (3–8):",
    options=numeric_cols,
    default=[c for c in ["Bevölkerung", "Bevölkerungs-dichte", "Unter 18-Jährige", "65-Jährige und Ältere"] if c in numeric_cols]
)

sel_for_profile = st.multiselect(
    "Районы для профиля:",
    options=merged["district"].sort_values().tolist(),
    default=merged["district"].sample(min(3, len(merged)), random_state=3).tolist()
)

if len(profile_cols) >= 3 and sel_for_profile:
    base = merged.set_index("district")
    sub = base.loc[sel_for_profile, profile_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)

    # Нормируем в 0..1 по столбцам (min-max)
    norm = (sub - sub.min()) / (sub.max() - sub.min() + 1e-9)
    long = norm.reset_index().melt(id_vars="district", var_name="feature", value_name="value")

    line = alt.Chart(long).mark_line(point=True).encode(
        x=alt.X("feature:N", title="Показатель"),
        y=alt.Y("value:Q", title="Норм. значение (0..1)"),
        color=alt.Color("district:N", legend=alt.Legend(title="Район")),
        tooltip=["district", "feature", alt.Tooltip("value:Q", format=".2f")]
    ).properties(height=420)

    st.altair_chart(line, use_container_width=True)
