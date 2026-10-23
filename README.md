# Sri Lanka Economic Snapshot Dashboard

A portfolio project built with **Python, Streamlit, Pandas, Plotly and pytest**.

## Features

- KPI cards for labour-force participation and unemployment.
- Interactive Plotly chart for comparing the two indicators over time.
- Official data table and CSV download.
- CSV uploader for exploring other public statistics.
- CSV validation helpers and automated pytest tests.
- GitHub Actions workflow for running tests on pushes and pull requests.

## Data sources

The bundled CSV contains labour-market figures published by the **Department of Census and Statistics (DCS), Sri Lanka**:

- **2025 annual:** labour-force participation rate 49.4%; unemployment rate 3.9%.
- **2026 Q1:** labour-force participation rate 49.2%; unemployment rate 3.7%.
- **2026 Q2:** labour-force participation rate 50.0%; unemployment rate 4.0%.

Sources: [DCS annual labour-force bulletins](https://www.statistics.gov.lk/LabourForce/StaticalInformation/Bulletins/) and [DCS quarterly labour-force reports](https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/). The DCS website lists these figures in its official releases.

These are published observations, not a live data feed. The dashboard displays the latest period included in the CSV; update the CSV when new official releases become available. The automated tests check data structure and validation, but do not independently verify figures against source publications.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Activate the environment, then install dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
pytest -q
```

GitHub Actions runs the tests automatically on pushes and pull requests.


## Vector tracking and exploration engine

The repository now includes `exploration_engine.py`, a dependency-free Python reference module implementing vector tracking, angle-threshold turn/change detection, and 2D occupancy-grid raycasting, plus `tests/test_exploration_engine.py` covering normal cases and invalid inputs.

- **Use case:** economic indicators; translate project measurements into 2D coordinates before interpreting the generic algorithm's results.
- **Run tests:** `python -m pytest -q`.
- **Scope:** this raycast is a generic grid primitive, not geographic collision avoidance, official aviation routing, medical advice, or real-world navigation.

The existing GitHub repository and live-demo URLs remain unchanged. Python is the implemented reference engine. C++23 with Conan/vcpkg, Rust, PHP/Symfony/Mago, and Django are not represented as integrated runtimes in this change; they should be added only as tested adapters where the project's architecture benefits from them, rather than forcing every framework into every app.


## Lightweight image and interaction performance

- Uses native browser image loading hints (`loading="lazy"`, `decoding="async"`) for non-first images to reduce off-screen work where image assets are present.
- Supports progressive WebP delivery when an image supplies a verified `data-webp-src`; browsers can also select WebP natively through `<picture><source type="image/webp">\` with a conventional fallback.
- Keeps responsive navigation interactions in native JavaScript rather than adding a large UI framework. Existing CSS-generated concept art remains CSS-based, avoiding extra image downloads.
- The helper is intentionally small and does not convert or invent image assets; WebP variants must exist before a `data-webp-src` is added.
