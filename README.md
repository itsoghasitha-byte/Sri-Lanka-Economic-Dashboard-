# Sri Lanka Economic Snapshot Dashboard

A portfolio project built with **Python, Streamlit, Pandas, Plotly and pytest**.

## Features

- KPI cards for labour-force participation and unemployment.
- Interactive Plotly chart for comparing the two indicators over time.
- Official data table and CSV download.
- CSV uploader for exploring other public statistics.
- Validation helpers and automated pytest tests.
- GitHub Actions workflow for running tests on pushes and pull requests.

## Data sources

The dashboard's bundled CSV contains these published figures from the **Department of Census and Statistics (DCS), Sri Lanka**:

- **2025 annual:** labour-force participation rate 49.4%; unemployment rate 3.9%.
- **2026 Q1:** labour-force participation rate 49.2%; unemployment rate 3.7%.

Sources:
- [DCS Labour Force Survey quarterly reports](https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/)
- [DCS official website](https://www.statistics.gov.lk/en)

The CSV records the source for each observation. These are published figures, not a live data feed; update the CSV when new official reports are released. Values and labels should be checked against the linked publications before reuse.

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
