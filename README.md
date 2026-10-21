# Sri Lanka Economic Snapshot Dashboard

A portfolio project built with **Python, Streamlit, Pandas, Plotly and pytest**.

## Features

- KPI cards for labour-force participation and unemployment.
- Interactive Plotly chart for comparing the two indicators over time.
- Official data table and CSV download.
- CSV uploader for exploring other public statistics.
- CSV validation helpers and automated pytest tests.
- AI research studio for web-grounded analysis of Sri Lankan finance, real estate, development and India–Sri Lanka business cooperation (requires an OpenAI API key).
- FastAPI backend with database-backed indicator search, research history, PostgreSQL/Supabase support and a secure server-side AI research endpoint.
- Holographic static website with a live API explorer and AI research interface.
- Frontend security checks and API route tests in GitHub Actions.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the Supabase, Render, GitHub Pages and secret configuration walkthrough. Hosted services still require setup in your own provider accounts.
- GitHub Actions workflow for running tests on pushes and pull requests.

## Data sources

The bundled CSV contains labour-market figures published by the **Department of Census and Statistics (DCS), Sri Lanka**:

- **2025 annual:** labour-force participation rate 49.4%; unemployment rate 3.9%.
- **2026 Q1:** labour-force participation rate 49.2%; unemployment rate 3.7%.
- **2026 Q2:** labour-force participation rate 50.0%; unemployment rate 4.0%.

Sources: [DCS annual labour-force bulletins](https://www.statistics.gov.lk/LabourForce/StaticalInformation/Bulletins/) and [DCS quarterly labour-force reports](https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/). The DCS website lists these figures in its official releases.

These are published observations, not a live data feed. The dashboard displays the latest period included in the CSV; update the CSV when new official releases become available. The automated tests check data structure and validation, but do not independently verify figures against source publications.

## AI research setup

The AI research studio uses the OpenAI Responses API with web search to research current public reports and provide source-linked analysis. To enable it, create an OpenAI API key and configure it as an environment variable named OPENAI_API_KEY, or add it in your Streamlit hosting provider's Secrets settings. Never commit the key to GitHub. The optional OPENAI_MODEL variable can override the default model.

Without a configured API key, the rest of the dashboard still works, but AI research requests will show setup instructions. AI output is not investment, legal or property advice; verify important claims against primary sources.

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
