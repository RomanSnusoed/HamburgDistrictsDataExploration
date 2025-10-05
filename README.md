# 🏙️ Hamburg Districts Data Explorer

An interactive **data visualization and analytics app** built with [Streamlit](https://streamlit.io/), showcasing demographic and statistical insights for **Hamburg's districts** using geospatial and tabular data.

---

## ✨ Features

- 🗺️ **Interactive Choropleth Map** — visualize any indicator on Hamburg's district map using Folium
- 📊 **Analytics Dashboard** — KPIs, Top/Bottom rankings, distributions, scatter plots
- 📈 **Bonus Insights** — compare districts vs. city average, KMeans clustering, normalized profiles
- 📑 **Dynamic Table View** — filter, search, and export CSV on the fly
- 🧠 **Clean Data Pipeline** — automatic parsing of complex raw CSV with multi-level headers

---

## 🧰 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Visualization**: [Folium](https://python-visualization.github.io/folium/), [Plotly](https://plotly.com/python/), [Altair](https://altair-viz.github.io/), [Matplotlib](https://matplotlib.org/)
- **Geospatial**: [GeoPandas](https://geopandas.org/), [OSMnx](https://osmnx.readthedocs.io/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/), [scikit-learn](https://scikit-learn.org/stable/) (for clustering)
- **Language**: Python 3.11+

---

## 📂 Project Structure

```
📦 project-root
├── 📁 src
│   ├── app.py                  # Main entry (map view)
│   ├── analytics.py            # Analytics dashboard (KPIs, plots)
│   ├── bonus.py                # Bonus insights (clustering, profiles)
│   ├── table.py                # Interactive table page
│   ├── data_loader.py          # CSV & Geo data loading
│   ├── dtpr.py                 # Data preparation (name cleanup, grouping)
│   ├── views_map.py            # Choropleth map rendering
│   └── views_charts.py         # Plotly/Matplotlib charts
├── 📁 data                     # Local CSV files and shapefiles
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/RomanSnusoed/HamburgDistrictsDataExploration.git
cd /repo
# Create virtual environment
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run src/app.py
```

Then open 👉 http://localhost:8501 in your browser.

---

## 📊 Data

**Source:** Official Hamburg statistics dataset (2022)\*\*  
Preprocessed with a custom Python script that parses multi-level headers, cleans values, and merges with geospatial boundaries.

---

## 🌟 Possible Extensions

- 📅 Add multi-year datasets and time-series comparisons
- 📊 Implement advanced clustering or PCA visualizations
- ☁️ Deploy to Streamlit Cloud or HuggingFace Spaces
- 🌍 Add custom indicators (economic, environmental, etc.)
