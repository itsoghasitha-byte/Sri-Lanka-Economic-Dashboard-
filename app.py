import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sri Lanka Economic Snapshot", page_icon="📊", layout="wide")
st.title("🇱🇰 Sri Lanka Economic Snapshot")
st.caption("A portfolio demo built with Streamlit, Pandas and Plotly.")

st.warning(
    "Demo data notice: the figures below are illustrative placeholders for demonstrating "
    "dashboard functionality. They are not verified official statistics and must not be "
    "used for reporting. Replace them with values checked against the linked DCS/CBSL publications."
)

labour = pd.DataFrame([
    {"Period": "2025 annual (demo)", "Labour force participation (%)": 49.4, "Unemployment (%)": 3.9},
    {"Period": "2026 Q1 (demo)", "Labour force participation (%)": 49.2, "Unemployment (%)": 3.7},
    {"Period": "2026 Q2 (demo)", "Labour force participation (%)": 50.0, "Unemployment (%)": 4.0},
])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Labour participation (demo)", "50.0%", "Example value")
c2.metric("Unemployment (demo)", "4.0%", "Example value")
c3.metric("NCPI index (demo)", "223.9", "Placeholder")
c4.metric("CCPI index (demo)", "209.1", "Placeholder")

st.divider()
left, right = st.columns([1.4, 1])
with left:
    st.subheader("Labour market indicators — demo data")
    metric = st.radio("Choose a measure", ["Labour force participation (%)", "Unemployment (%)"], horizontal=True)
    fig = px.line(labour, x="Period", y=metric, markers=True, title=f"{metric} — illustrative values",
                  labels={"Period": "Reporting period", metric: metric})
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10), yaxis_title="Percent", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Underlying example data")
    st.dataframe(labour, use_container_width=True, hide_index=True)
    st.download_button("Download example labour data (CSV)", data=labour.to_csv(index=False).encode("utf-8"),
                       file_name="sri_lanka_labour_indicators_demo.csv", mime="text/csv")

st.divider()
st.subheader("Explore your own CSV")
st.write("Upload a public DCS/CBSL table or another CSV. The file should contain at least one numeric column.")
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
            y_cols = st.multiselect("Numeric measures to chart", numeric_cols,
                                    default=numeric_cols[:min(2, len(numeric_cols))])
            if y_cols:
                if x_col == "(row number)":
                    plot_data = data.copy()
                    plot_data["Row"] = range(1, len(plot_data) + 1)
                    fig2 = px.line(plot_data, x="Row", y=y_cols, markers=True)
                else:
                    fig2 = px.line(data, x=x_col, y=y_cols, markers=True)
                fig2.update_layout(margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.caption("Select at least one numeric measure to create a chart.")
    except Exception as exc:
        st.error(f"Could not read this CSV: {exc}")

st.caption("Reference sources for replacing demo values with verified data:")
st.markdown(
    "- [Department of Census and Statistics — official website](https://www.statistics.gov.lk/en)\n"
    "- [DCS — statistics portal](https://www.statistics.gov.lk/)\n"
    "- [Central Bank of Sri Lanka — economic indicators](https://www.cbsl.gov.lk/en/statistics/economic-indicators)"
)
