from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_csv, validate_labour_data

st.set_page_config(page_title="Sri Lanka Economic Snapshot", page_icon="📊", layout="wide")

st.markdown("""
<style>
:root { color-scheme: light; }
.stApp { background: #f4f1e8; color: #20352d; }
[data-testid="stHeader"] { background: rgba(244,241,232,.94); }
[data-testid="stSidebar"] { background: #e6eee5; }
.block-container { padding-top: 2rem; max-width: 1450px; }
h1,h2,h3 { color: #173f35 !important; letter-spacing: -.025em; }
[data-testid="stMetric"] { background: #fffdf7; border: 1px solid #d6e0d4; border-radius: 14px; padding: 18px 20px; box-shadow: 0 5px 18px #173f350b; }
[data-testid="stMetricLabel"] { color: #61766b !important; }
[data-testid="stMetricValue"] { color: #16745b !important; }
.stButton button, .stDownloadButton button { background: #176b55; color: #fffdf7; border: 1px solid #176b55; border-radius: 9px; }
.stButton button:hover, .stDownloadButton button:hover { background: #0f5141; color: #fff; border-color: #0f5141; }
[data-testid="stFileUploader"] { background: #fffdf7; border: 1px dashed #9bb8a6; border-radius: 12px; padding: 10px; }
hr { border-color: #d6e0d4; }
</style>
""", unsafe_allow_html=True)
st.title("🇱🇰 Sri Lanka Economic Snapshot")
st.caption("Sri Lankan labour-market indicators from official Department of Census and Statistics publications.")

DATA_FILE = Path(__file__).parent / "data" / "labour_indicators.csv"
SOURCE_TEXT = (
    "Source: Department of Census and Statistics, Sri Lanka Labour Force Survey "
    "(2025 Annual Bulletin, 1st Quarter 2026 report and 2nd Quarter 2026 bulletin)."
)
DCS_URL = "https://www.statistics.gov.lk/LabourForce/StaticalInformation/Bulletins/"

try:
    with DATA_FILE.open("r", encoding="utf-8") as csv_file:
        labour = validate_labour_data(load_csv(csv_file))
except Exception as exc:
    st.error(f"Could not load the official labour data file: {exc}")
    st.stop()

latest = labour.iloc[-1]
c1, c2, c3 = st.columns(3)
c1.metric("Labour participation", f"{latest['Labour force participation (%)']:.1f}%")
c2.metric("Unemployment rate", f"{latest['Unemployment (%)']:.1f}%")
c3.metric("Latest reporting period", str(latest["Period"]))

st.divider()
left, right = st.columns([1.4, 1])
with left:
    st.subheader("Labour-market trends")
    metric = st.radio(
        "Choose a measure",
        ["Labour force participation (%)", "Unemployment (%)"],
        horizontal=True,
    )
    fig = px.line(
        labour,
        x="Period",
        y=metric,
        markers=True,
        title=metric,
        labels={"Period": "Reporting period", metric: metric},
    )
    fig.update_traces(line_color="#168064", marker_color="#d18b37", line_width=3)
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#fffdf7",
        plot_bgcolor="#fffdf7",
        font_color="#20352d",
        margin=dict(l=10, r=10, t=55, b=10),
        yaxis_title="Percent",
        xaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(SOURCE_TEXT)
    st.markdown(f"[View official DCS labour-force bulletins]({DCS_URL})")

with right:
    st.subheader("Official data table")
    st.dataframe(labour, use_container_width=True, hide_index=True)
    st.download_button(
        "Download official labour data (CSV)",
        data=labour.to_csv(index=False).encode("utf-8"),
        file_name="sri_lanka_labour_indicators.csv",
        mime="text/csv",
    )

st.divider()
st.subheader("Explore another CSV")
st.write("Upload a public statistics CSV. It should contain at least one numeric column.")
uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded is not None:
    try:
        data = pd.read_csv(uploaded)
        st.write("Preview")
        st.dataframe(data.head(20), use_container_width=True)
        numeric_cols = data.select_dtypes(include="number").columns.tolist()
        all_cols = data.columns.tolist()
        if not numeric_cols:
            st.warning("No numeric columns were found. Check the CSV format.")
        else:
            x_options = ["(row number)"] + all_cols
            x_col = st.selectbox("X-axis / category", x_options, index=0)
            y_cols = st.multiselect(
                "Numeric measures to chart",
                numeric_cols,
                default=numeric_cols[:min(2, len(numeric_cols))],
            )
            if y_cols:
                if x_col == "(row number)":
                    plot_data = data.copy()
                    plot_data["Row"] = range(1, len(plot_data) + 1)
                    fig2 = px.line(plot_data, x="Row", y=y_cols, markers=True)
                else:
                    fig2 = px.line(data, x=x_col, y=y_cols, markers=True)
                fig2.update_traces(line_color="#168064", marker_color="#d18b37", line_width=3)\n                fig2.update_layout(template="plotly_white", paper_bgcolor="#fffdf7", plot_bgcolor="#fffdf7", font_color="#20352d", margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.caption("Select at least one numeric measure to create a chart.")
    except Exception as exc:
        st.error(f"Could not read this CSV: {exc}")
