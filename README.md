# UrbanEcoViz

UrbanEcoViz — production-ready Streamlit-приложение для 3D-визуализации экологических данных Гамбурга. Проект использует реальные
наборы с портала [Transparenz Hamburg](https://suche.transparenz.hamburg.de) и демонстрирует, как объединять показатели загрязнения
воздуха и дорожного трафика на интерактивной карте Pydeck.

## 🚀 Основные возможности
- Загрузка официальных CSV/GeoJSON наборов: концентрации NO₂/PM₁₀/O₃, дорожный трафик и границы районов.
- Нормализация показателей в диапазоне 0–1 для сопоставимых высот 3D-колонок.
- Streamlit-интерфейс с выбором показателя (NO₂, PM₁₀, Traffic) и года, а также всплывающими тултипами.
- Production-инфраструктура: Dockerfile, GitHub Actions (pytest + flake8), автогенерация pydeck карт.

## 🗂 Структура проекта
```
UrbanEcoViz/
├── data/
│   ├── hamburg_districts.geojson   # Геометрия районов (EPSG:4326)
│   ├── luftschadstoffe_hamburg.csv # Концентрации NO₂, PM₁₀, O₃ по станциям замеров
│   └── verkehrsbelastung_hamburg.csv # Среднегодовая нагрузка на дорожную сеть
├── notebooks/                      # Jupyter-исследования (при необходимости)
├── src/
│   ├── app.py                      # Точка входа Streamlit-приложения
│   ├── data_loader.py              # Загрузка и валидация датасетов
│   ├── preprocessing.py            # Нормализация и агрегации по районам
│   └── visualization.py            # Функции построения pydeck-слоёв
├── tests/                          # Pytest-тесты пайплайна
├── Dockerfile                      # Контейнер для деплоя (Streamlit)
├── requirements.txt                # Зависимости Python 3.11
└── .github/workflows/ci.yml        # CI: lint + тесты
```

## 📦 Установка и запуск
### Локально (Windows 11 / macOS / Linux)
```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
source .venv/bin/activate   # macOS/Linux
pip install --upgrade pip
pip install -r requirements.txt
streamlit run src/app.py
```
После запуска приложение будет доступно по адресу http://localhost:8501 и отобразит 3D-карту с реальными данными NO₂/PM₁₀/Traffic.

### Через Docker
```bash
docker build -t urbanecoviz .
docker run -it --rm -p 8501:8501 urbanecoviz
```

### Деплой на Streamlit Cloud
1. Опубликуйте репозиторий на GitHub.
2. На [streamlit.io/cloud](https://streamlit.io/cloud) создайте приложение и укажите `src/app.py`.
3. В разделе “Advanced settings” установите переменную `PYTHON_VERSION=3.11` (по желанию) и деплойте.

### Деплой на Render
1. Создайте новый **Web Service** и выберите Python 3.11.
2. Команда запуска: `streamlit run src/app.py --server.port $PORT --server.address 0.0.0.0`.
3. Включите авто-деплой из main-ветки.

## 🧪 Разработка и тестирование
```bash
flake8 src tests
pytest
```
Обе команды выполняются в GitHub Actions (workflow `.github/workflows/ci.yml`).

## 🔍 Примеры использования
```python
from src.data_loader import load_pollution_data
from src.preprocessing import aggregate_pollution_by_district, normalize_metrics

pollution = load_pollution_data()
aggregated = aggregate_pollution_by_district(pollution)
normalized = normalize_metrics(aggregated, group_by=["indicator", "year"])
print(normalized.head())
```

## 🔗 Открытые источники данных
- [Luftschadstoffe Hamburg (NO₂, PM₁₀, O₃)](https://suche.transparenz.hamburg.de/dataset/luftschadstoffe-hamburg) — оригинальный CSV.
- [Verkehrsbelastung Hamburg](https://suche.transparenz.hamburg.de/dataset/verkehrsbelastung-hamburg) — среднегодовой трафик по районам.
- [Hamburg District Boundaries (OpenStreetMap/Transparenz Hamburg)](https://suche.transparenz.hamburg.de/dataset/hamburg-stadtteile-geojson).

## 🗺 Roadmap
- [ ] Интеграция ML-прогноза загрязнения и трафика на горизонте 7 дней.
- [ ] Анимация временных рядов Pydeck и экспорт GIF/MP4.
- [ ] Поддержка дополнительных индикаторов (например, шумовое загрязнение, энергетика).

## 🤝 Вклад
Pull Request'ы приветствуются! Перед отправкой обновите документацию (при необходимости) и убедитесь, что `flake8` и `pytest` проходят
локально или в CI.
