# Sri Lanka Economic Intelligence

An AI-assisted Sri Lankan economic research and data dashboard built with **Python, Streamlit, FastAPI, PostgreSQL, Pandas, Plotly and pytest**.

## Features

- Labour-market KPI cards and interactive time-series visualisations.
- CSV data explorer, downloads, upload validation and automated data-quality checks.
- AI research studio for web-grounded analysis of Sri Lankan finance, real estate, development and India–Sri Lanka business cooperation (requires a server-side OpenAI API key).
- FastAPI endpoints for indicator search, research history and AI research.
- Searchable AI-generated knowledge pages with source links and revision history.
- PostgreSQL support, with SQLite for local development.
- Holographic static website, API explorer and GitHub Actions test workflow.

## Official labour-market data

The bundled data/labour_indicators.csv contains these observations published by Sri Lanka's **Department of Census and Statistics (DCS)**:

| Period | Labour-force participation | Unemployment |
|---|---:|---:|
| 2025 annual | 49.4% | 3.9% |
| 2026 Q1 | 49.2% | 3.7% |
| 2026 Q2 | 50.0% | 4.0% |

The values above are cross-checked against DCS official releases and landing-page summaries. See [DCS labour-force bulletins](https://www.statistics.gov.lk/LabourForce/StaticalInformation/Bulletins/) and [DCS quarterly reports](https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/). Source directories can change; the CSV records the relevant official landing page for each observation. The review date and limitations are documented in [data/SOURCES.md](data/SOURCES.md).

**Freshness limitation:** this is a bundled snapshot, not a live data feed. New official releases do not automatically change the CSV. Update data only after checking the corresponding primary publication. Automated tests check expected periods, values, source domains and data shape; they do not download publications or independently reproduce the source tables.

## AI research and knowledge base

The API can use the OpenAI Responses API with web search to answer research questions and create or refresh knowledge pages. Pages are saved with source URLs and revision history. AI-generated content can be incomplete or incorrect, so users should verify important claims against linked primary sources.

AI features require OPENAI_API_KEY configured **server-side**. Never place the key in browser JavaScript or commit it to the repository. Without the key, AI endpoints return a configuration error; non-AI dashboard functionality remains available.

## Run locally

Python 3.10 or newer is recommended.

    python -m venv .venv
    pip install -r requirements.txt
    streamlit run app.py

The API can be run separately with:

    uvicorn api.main:app --reload

## Tests

    pytest -q

GitHub Actions compiles Python, checks JavaScript syntax and runs the automated test suite on pushes and pull requests.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for database, API, frontend and secret configuration. A GitHub Pages workflow is included at `.github/workflows/deploy-pages.yml` for a free static preview; enable **Settings → Pages → GitHub Actions** in the repository for that workflow to publish. GitHub Pages serves only the frontend files: AI research and database features require a separately deployed API, a configured API URL, and server-side `OPENAI_API_KEY`/`DATABASE_URL` secrets. Hosted services must be provisioned in the relevant provider accounts; a GitHub commit alone does not deploy the application. The premium frontend/API work is currently on the feature/premium-economic-website branch until merged.
