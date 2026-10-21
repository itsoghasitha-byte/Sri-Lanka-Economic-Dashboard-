# Sri Lanka Economic Snapshot Dashboard

A beginner-friendly portfolio project built with **Python, Streamlit, Pandas, Plotly and pytest**.

## Features

- KPI cards and an interactive Plotly line chart.
- Pandas data table and CSV download.
- CSV uploader for exploring public statistics tables.
- Validation helpers for missing, malformed and out-of-range labour indicator data.
- Automated pytest suite and GitHub Actions workflow.

## Important data note

The dashboard currently uses **illustrative demo values** to demonstrate the UI. They are not verified official statistics, are not connected to a live API, and must not be used for reporting or decision-making. Replace the demo values with figures verified against an official publication before presenting the dashboard as an analysis of Sri Lanka's economy.

Official sources to consult:
- Department of Census and Statistics: https://www.statistics.gov.lk/en
- DCS statistics portal: https://www.statistics.gov.lk/
- Central Bank of Sri Lanka economic indicators: https://www.cbsl.gov.lk/en/statistics/economic-indicators

## Run locally

Python 3.10 or newer is recommended.

\`\`\`bash
python -m venv .venv
\`\`\`

Activate the environment, then install dependencies and start the app:

\`\`\`bash
pip install -r requirements.txt
streamlit run app.py
\`\`\`

## Run tests

\`\`\`bash
pytest -q
\`\`\`

GitHub Actions runs the tests automatically on pushes and pull requests.

## Deploy with Streamlit Community Cloud

1. Sign in at https://share.streamlit.io/ using GitHub.
2. Create a new app and select this repository.
3. Choose the \`main\` branch and \`app.py\` as the main file.
4. Deploy the app.

## Next improvements

- Replace placeholders with verified downloadable DCS/CBSL data.
- Add data-source dates and citations beside each metric.
- Expand tests for duplicate columns, blank periods and malformed CSV uploads.
