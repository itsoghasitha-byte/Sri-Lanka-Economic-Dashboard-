from pathlib import Path
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from data_utils import load_csv, validate_labour_data
from ai_research import research_with_ai

st.set_page_config(
    page_title="Sri Lanka Economic Intelligence",
    page_icon="🇱🇰",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "data" / "labour_indicators.csv"
DCS_BULLETINS = "https://www.statistics.gov.lk/LabourForce/StaticalInformation/Bulletins/"
DCS_QUARTERLY = "https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/"
SOURCE_TEXT = (
    "Department of Census and Statistics (DCS), Sri Lanka — Labour Force Survey "
    "bulletins and quarterly reports. Bundled observations are published figures, "
    "not a live data feed."
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink:#17212e; --muted:#66758b; --teal:#76e7da; --blue:#2e6bff; --chrome:linear-gradient(115deg,#59636f 0%,#f8fbff 18%,#8995a3 34%,#ffffff 49%,#77828f 65%,#e8edf2 82%,#5e6874 100%); }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background:linear-gradient(180deg,#f5f8fc 0%,#edf3f9 100%); }
    [data-testid="stHeader"] { background:rgba(245,248,252,.88); }
    .block-container { padding-top:1.7rem; padding-bottom:3rem; max-width:1500px; }
    h1,h2,h3 { font-family:'Manrope',sans-serif!important; color:var(--ink); letter-spacing:-.035em; font-weight:750!important; }
    h1 { font-size:2.35rem!important; font-weight:800!important; }
    h2 { font-weight:750!important; }
    .stApp h1:not(.hero h1), .stApp h2, .stApp h3 { background:linear-gradient(110deg,#59636f 0%,#b7c0ca 24%,#46515e 48%,#aab4bf 72%,#58626f 100%); -webkit-background-clip:text; background-clip:text; color:transparent!important; -webkit-text-fill-color:transparent; text-shadow:none!important; }
    [data-testid="stMetricValue"] { background:linear-gradient(110deg,#697480,#1f2935 45%,#7d8792); -webkit-background-clip:text; background-clip:text; color:transparent!important; -webkit-text-fill-color:transparent; }
    [data-testid="stMetric"] { background:#fff; padding:1.15rem 1.2rem; border:1px solid #e2eaf3; border-radius:18px; box-shadow:0 8px 26px rgba(21,45,78,.045); }
    [data-testid="stMetricLabel"] { color:#66758b; font-weight:600; }
    [data-testid="stMetricValue"] { font-family:'Manrope',sans-serif; font-weight:800; }
    [data-testid="stTabs"] button { font-weight:700; }
    .hero { padding:2.1rem 2.2rem; border-radius:26px; color:#fff; background:radial-gradient(circle at 85% 20%,rgba(54,214,189,.32),transparent 28%),linear-gradient(120deg,#0d1f3c 0%,#123e70 55%,#146a79 100%); box-shadow:0 18px 50px rgba(18,50,86,.18); margin:.2rem 0 1.25rem 0; }
    .hero-kicker { text-transform:uppercase; letter-spacing:.16em; color:#85f1df; font-size:.73rem; font-weight:800; }
    .hero h1 { background:linear-gradient(115deg,#e8edf2 0%,#ffffff 18%,#aeb8c3 35%,#ffffff 52%,#9ca8b5 70%,#f4f7fa 86%,#aab4be 100%); -webkit-background-clip:text; background-clip:text; color:transparent!important; -webkit-text-fill-color:transparent; text-shadow:none!important; margin:.55rem 0 .7rem 0; font-size:clamp(2rem,4vw,3.5rem)!important; line-height:1.06; max-width:850px; }
    .hero p { color:#d7e5f4; max-width:760px; font-size:1.02rem; line-height:1.7; }
    .hero-foot { color:#9bb5ce; font-size:.78rem; margin-top:1.2rem; }
    .section-eyebrow { color:#287f83; font-size:.72rem; text-transform:uppercase; letter-spacing:.14em; font-weight:800; margin-bottom:.25rem; }
    .panel { background:#fff; border:1px solid #e2eaf3; border-radius:20px; padding:1.25rem 1.35rem; box-shadow:0 8px 26px rgba(21,45,78,.035); }
    .photo-intro { margin:1.7rem 0 .8rem; padding-top:.5rem; }
    .photo-card { background:#fff; border:1px solid #dce3eb; border-radius:16px; padding:.6rem; margin-bottom:1rem; box-shadow:0 10px 26px rgba(15,27,42,.06); }
    .photo-card img { border-radius:11px; object-fit:cover; }
    .photo-card a { font-size:.78rem; }
    .panel-title { color:#10233f; font-family:'Manrope',sans-serif; font-weight:800; font-size:1.08rem; margin-bottom:.45rem; }
    .muted { color:#66758b; font-size:.9rem; line-height:1.65; }
    .source-pill { display:inline-block; border:1px solid rgba(54,214,189,.45); color:#b7fff2; background:rgba(54,214,189,.1); padding:.35rem .7rem; border-radius:999px; font-size:.75rem; font-weight:700; }
    .callout { border-left:4px solid #36d6bd; background:#e8f8f5; border-radius:0 12px 12px 0; padding:.85rem 1rem; color:#244d56; line-height:1.6; }
    div[data-testid="stDownloadButton"] button { border-radius:10px; font-weight:700; }
    a { color:#176b9a!important; font-weight:600; }
    footer { visibility:hidden; }
    @media (max-width:700px) { .hero { padding:1.35rem; border-radius:19px; } .block-container { padding-left:1rem; padding-right:1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    with DATA_FILE.open("r", encoding="utf-8") as csv_file:
        labour = validate_labour_data(load_csv(csv_file))
except Exception as exc:
    st.error(f"Could not load the official labour data file: {exc}")
    st.stop()

latest = labour.iloc[-1]
previous = labour.iloc[-2] if len(labour) > 1 else None

if st.session_state.get("nav_target"):
    st.session_state["page"] = st.session_state.pop("nav_target")

with st.sidebar:
    st.markdown("## 🇱🇰 SL / ECON")
    st.caption("ECONOMIC INTELLIGENCE")
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Labour-market trends", "Data explorer", "AI research studio", "Sources & methodology"],
        label_visibility="collapsed",
        key="page",
    )
    st.divider()
    st.markdown("**DATA STATUS**")
    st.success("Local dataset loaded")
    st.caption(f"{len(labour)} reporting periods · Official published observations")
    st.markdown("---")
    st.caption("Built with Python · Streamlit · Pandas · Plotly")
    st.caption("Figures are not updated automatically.")

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-kicker">Sri Lanka · Public statistics · Research dashboard</div>
      <h1>Understand the economy.<br>One indicator at a time.</h1>
      <p>An interactive, source-aware look at Sri Lanka's labour market, designed to make official statistics easier to explore, compare and download.</p>
      <span class="source-pill">OFFICIAL SOURCE-REFERENCED DATA</span>
      <div class="hero-foot">LATEST INCLUDED PERIOD: {latest['Period']} &nbsp; • &nbsp; DATASET: LABOUR-MARKET INDICATORS</div>
    </div>
    """,
    unsafe_allow_html=True,
)



if page == "Overview":

    st.markdown(
        """
        <div class="photo-intro">
          <div class="section-eyebrow">03 / Island field notes</div>
          <h2>One island. Many perspectives.</h2>
          <p class="muted">A curated photographic journey through Sri Lanka. Select a location to explore the original photograph and its source record.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    photo_items = {
        "Sigiriya": ("https://commons.wikimedia.org/wiki/Special:FilePath/Aerial%20View%20from%20Sigiriya.jpg?width=1400", "https://commons.wikimedia.org/wiki/File:Aerial_View_from_Sigiriya.jpg"),
        "Mirissa Beach": ("https://commons.wikimedia.org/wiki/Special:FilePath/Mirissa%20beach%2C%20Srilanka.jpg?width=1400", "https://commons.wikimedia.org/wiki/File:Mirissa_beach,_Srilanka.jpg"),
        "Galle Fort": ("https://commons.wikimedia.org/wiki/Special:FilePath/Galle%20Fort%20-%20Srilanka.jpg?width=1400", "https://commons.wikimedia.org/wiki/File:Galle_Fort_-Srilanka.jpg"),
        "Colombo Lotus Tower": ("https://commons.wikimedia.org/wiki/Special:FilePath/Colombo%20Lotus%20Tower%20seen%20Galle%20Road.jpg?width=1400", "https://commons.wikimedia.org/wiki/File:Colombo_Lotus_Tower_seen_Galle_Road.jpg"),
        "Ella": ("https://commons.wikimedia.org/wiki/Special:FilePath/Ella%2C%20Sri%20Lanka.jpg?width=1400", "https://commons.wikimedia.org/wiki/File:Ella,_Sri_Lanka.jpg"),
        "Parliament aerial": ("https://commons.wikimedia.org/wiki/Special:FilePath/New%20Sri%20Lankan%20Parliament%20in%20Kotte.jpg?width=1400", "https://commons.wikimedia.org/wiki/File:New_Sri_Lankan_Parliament_in_Kotte.jpg"),
        "Galle Face Green": ("https://commons.wikimedia.org/wiki/Special:FilePath/Colombo%20Galle%20Face%20Green.jpg?width=1400", "https://commons.wikimedia.org/wiki/File:Colombo_Galle_Face_Green.jpg"),
    }
    photo_location = st.radio(
        "Choose a destination",
        list(photo_items.keys()),
        horizontal=True,
        key="photo_location",
    )
    photo_url, source_url = photo_items[photo_location]
    image_col, details_col = st.columns([1.65, 1], gap="large")
    with image_col:
        st.image(photo_url, use_container_width=True)
    with details_col:
        st.markdown(f'<div class="panel-title">{photo_location}</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="muted">Real-photo source: Wikimedia Commons. Open the original file page to confirm photographer credit, licence conditions and permitted reuse before publishing.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(f"[View original photo and licence ↗]({source_url})")
        st.caption("Aerial image availability does not guarantee that it is a drone photograph. Replace with a verified drone-original if that exact viewpoint is required.")

    st.markdown('<div class="section-eyebrow">01 / Executive snapshot</div>', unsafe_allow_html=True)
    st.header("The labour market at a glance")
    st.write("Start with the latest reporting period in the bundled dataset, then move into the trends and underlying figures.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Labour-force participation",
        f"{latest['Labour force participation (%)']:.1f}%",
        delta=(
            f"{latest['Labour force participation (%)'] - previous['Labour force participation (%)']:+.1f} pp vs prior period"
            if previous is not None else None
        ),
        help="Percentage of the relevant population that is in the labour force.",
    )
    c2.metric(
        "Unemployment rate",
        f"{latest['Unemployment (%)']:.1f}%",
        delta=(
            f"{latest['Unemployment (%)'] - previous['Unemployment (%)']:+.1f} pp vs prior period"
            if previous is not None else None
        ),
        delta_color="inverse",
        help="Unemployment rate as published for the reporting period.",
    )
    c3.metric("Periods available", f"{len(labour)}", help="Number of periods included in the local CSV.")
    c4.metric("Latest period", str(latest["Period"]), help="Newest period present in the dataset, not a live update.")

    st.markdown("")
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.markdown('<div class="panel-title">Labour-market trajectory</div>', unsafe_allow_html=True)
        overview_metric = st.selectbox(
            "Choose an indicator",
            ["Labour force participation (%)", "Unemployment (%)"],
            key="overview_metric",
        )
        fig = px.line(
            labour, x="Period", y=overview_metric, markers=True,
            template="plotly_dark",
            labels={"Period": "Reporting period", overview_metric: "Percent"},
        )
        fig.update_traces(line=dict(width=3, color="#69e8ff"), marker=dict(size=9, color="#d4fff9", line=dict(width=2, color="#3a9dff")))
        fig.update_layout(
            height=350, margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="#071321", plot_bgcolor="#071321",
            font=dict(family="DM Sans", color="#c8dff0"),
            yaxis=dict(ticksuffix="%", gridcolor="rgba(92,180,230,.18)", zerolinecolor="rgba(92,180,230,.25)"),
            xaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown('<div class="panel-title">How to read this snapshot</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <p class="muted">These indicators describe different parts of the labour market. Participation measures how much of the relevant population is active in the labour force; unemployment measures the share of the labour force without work under the published statistical definition.</p>
            <div class="callout"><b>Important context</b><br>Small changes should be interpreted alongside the survey period, methodology and official release notes. A chart alone does not explain why an indicator moved.</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.markdown(f"[Open DCS labour-force bulletins ↗]({DCS_BULLETINS})")
        st.markdown(f"[Open DCS quarterly reports ↗]({DCS_QUARTERLY})")

    st.markdown("---")
    st.markdown('<div class="section-eyebrow">02 / Explore the report</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        st.markdown('<div class="panel"><div class="panel-title">01 · Trends</div><p class="muted">Compare indicators across reporting periods with interactive charts and filters.</p></div>', unsafe_allow_html=True)
        if st.button("Explore trends →", use_container_width=True):
            st.session_state["page"] = "Labour-market trends"
            st.rerun()
    with b:
        st.markdown('<div class="panel"><div class="panel-title">02 · Data explorer</div><p class="muted">Inspect the source table, download CSV data or chart another public statistics file.</p></div>', unsafe_allow_html=True)
        if st.button("Explore data →", use_container_width=True):
            st.session_state["page"] = "Data explorer"
            st.rerun()
    with c:
        st.markdown('<div class="panel"><div class="panel-title">03 · Methodology</div><p class="muted">Review source links, dataset limitations and how to reproduce the project locally.</p></div>', unsafe_allow_html=True)
        if st.button("View methodology →", use_container_width=True):
            st.session_state["page"] = "Sources & methodology"
            st.rerun()

elif page == "Labour-market trends":
    st.markdown('<div class="section-eyebrow">02 / Interactive analysis</div>', unsafe_allow_html=True)
    st.header("Labour-market trends")
    st.write("Select the indicators and chart style you want to examine. Hover over chart marks for exact values.")
    metric_options = ["Labour force participation (%)", "Unemployment (%)"]
    selected_metrics = st.multiselect("Indicators", metric_options, default=metric_options)
    chart_style = st.radio(
        "Visualisation",
        options=["Line", "Bar"],
        horizontal=True,
        key="trend_chart_style",
    )
    if not selected_metrics:
        st.info("Choose at least one indicator to draw a chart.")
    else:
        chart_data = labour.melt(
            id_vars=["Period"], value_vars=selected_metrics,
            var_name="Indicator", value_name="Percent",
        )
        if chart_style == "Bar":
            fig = px.bar(chart_data, x="Period", y="Percent", color="Indicator", barmode="group", template="plotly_dark")
        else:
            fig = px.line(chart_data, x="Period", y="Percent", color="Indicator", markers=True, template="plotly_dark")
        fig.update_layout(
            height=500, margin=dict(l=10, r=10, t=35, b=10),
            paper_bgcolor="#071321", plot_bgcolor="#071321",
            font=dict(family="DM Sans", color="#c8dff0"),
            yaxis=dict(title="Percent", ticksuffix="%", gridcolor="rgba(92,180,230,.18)", zerolinecolor="rgba(92,180,230,.25)"),
            xaxis=dict(title="Reporting period", showgrid=False),
            legend_title_text="Indicator",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.download_button(
            "Download chart data (CSV)",
            data=chart_data.to_csv(index=False).encode("utf-8"),
            file_name="sri_lanka_labour_chart_data.csv",
            mime="text/csv",
        )
    st.caption(SOURCE_TEXT)

elif page == "Data explorer":
    st.markdown('<div class="section-eyebrow">03 / Dataset laboratory</div>', unsafe_allow_html=True)
    st.header("Explore the underlying data")
    st.write("Review the bundled dataset or upload another CSV containing public statistics.")
    with st.expander("Bundled labour-market dataset", expanded=True):
        st.dataframe(labour, use_container_width=True, hide_index=True)
        st.download_button(
            "Download official labour data (CSV)",
            data=labour.to_csv(index=False).encode("utf-8"),
            file_name="sri_lanka_labour_indicators.csv",
            mime="text/csv",
            key="download_bundled",
        )
    st.markdown("---")
    st.subheader("Bring your own CSV")
    st.caption("Upload a public statistics CSV. Check its source and units before interpreting the results.")
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded is not None:
        try:
            data = pd.read_csv(uploaded)
            st.markdown("**Preview**")
            st.dataframe(data.head(50), use_container_width=True, hide_index=True)
            numeric_cols = data.select_dtypes(include="number").columns.tolist()
            all_cols = data.columns.tolist()
            if data.empty:
                st.warning("This CSV contains no data rows.")
            elif not numeric_cols:
                st.warning("No numeric columns were found. Check the CSV format.")
            else:
                x_col = st.selectbox("Category / X-axis", ["(row number)"] + all_cols)
                y_cols = st.multiselect(
                    "Numeric measures",
                    numeric_cols,
                    default=numeric_cols[:min(2, len(numeric_cols))],
                )
                chart_type = st.selectbox("Chart type", ["Line", "Bar", "Scatter"])
                if y_cols:
                    plot_data = data.copy()
                    if x_col == "(row number)":
                        plot_data["Row"] = range(1, len(plot_data) + 1)
                        x_axis = "Row"
                    else:
                        x_axis = x_col
                    if chart_type == "Bar":
                        fig = px.bar(plot_data, x=x_axis, y=y_cols, barmode="group", template="plotly_white")
                    elif chart_type == "Scatter":
                        fig = px.scatter(plot_data, x=x_axis, y=y_cols, template="plotly_white")
                    else:
                        fig = px.line(plot_data, x=x_axis, y=y_cols, markers=True, template="plotly_white")
                    fig.update_layout(height=430, margin=dict(l=10, r=10, t=25, b=10), paper_bgcolor="#071321", plot_bgcolor="#071321", font=dict(family="DM Sans", color="#c8dff0"), yaxis=dict(gridcolor="rgba(92,180,230,.18)"), xaxis=dict(gridcolor="rgba(92,180,230,.10)"))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Select at least one numeric measure to create a chart.")
        except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as exc:
            st.error(f"Could not read this CSV. Check that it is a valid, consistently formatted file. Details: {exc}")

elif page == "Sources & methodology":
    st.markdown('<div class="section-eyebrow">04 / Transparency & reproducibility</div>', unsafe_allow_html=True)
    st.header("Sources & methodology")
    st.write("This section documents where the included observations come from, what this dashboard does and does not claim, and how to reproduce it.")
    st.subheader("Primary sources")
    st.markdown(f"- [Department of Census and Statistics — Labour-force bulletins]({DCS_BULLETINS})")
    st.markdown(f"- [Department of Census and Statistics — Quarterly labour-force reports]({DCS_QUARTERLY})")
    st.info(SOURCE_TEXT)
    st.subheader("Dataset notes")
    st.markdown(
        """
        - The dashboard reads a local CSV file bundled with the repository.
        - Figures are displayed as published observations and are not a live data feed.
        - The latest displayed period is the last row after the project's data validation step.
        - Automated tests validate data structure and helper behaviour; they do not independently certify each value against a source publication.
        - Differences across periods should be interpreted with the relevant DCS definitions, survey design and release notes.
        """
    )
    st.subheader("Technology")
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Language", "Python")
    t2.metric("App framework", "Streamlit")
    t3.metric("Visualisation", "Plotly")
    t4.metric("Testing", "pytest")
    st.subheader("Run the project locally")
    st.code(
        "python -m venv .venv\n"
        "# Activate the environment, then run:\n"
        "pip install -r requirements.txt\n"
        "streamlit run app.py\n\n"
        "# Run automated tests:\n"
        "pytest -q",
        language="bash",
    )
    st.markdown("[View the repository on GitHub ↗](https://github.com/itsoghasitha-byte/Sri-Lanka-Economic-Dashboard-)")

elif page == "AI research studio":
    st.markdown('<div class="section-eyebrow">05 / Evidence-led research</div>', unsafe_allow_html=True)
    st.header("AI research studio")
    st.write("Ask a research question across Sri Lanka's finance, investment, real estate, infrastructure and business markets. The assistant searches the web and should cite the sources behind its analysis.")
    with st.expander("Research areas and suggested questions", expanded=True):
        prompt_cols = st.columns(2)
        with prompt_cols[0]:
            st.markdown("**Finance & development**")
            st.markdown("- What do the latest Central Bank and IMF reports say about inflation, debt, credit and growth?")
            st.markdown("- Which sectors could benefit from new foreign direct investment?")
            st.markdown("- What are the main risks for SMEs, exporters and capital markets?")
        with prompt_cols[1]:
            st.markdown("**Real estate & India partnership**")
            st.markdown("- What official evidence is available on Colombo office, residential, hospitality and logistics development?")
            st.markdown("- How could India-Sri Lanka energy, port, digital-payment and connectivity projects affect businesses?")
            st.markdown("- What is confirmed versus proposed in cooperation between President Anura Kumara Disanayaka and PM Narendra Modi?")
    with st.expander("Primary-source quick links", expanded=False):
        st.markdown("- [Central Bank of Sri Lanka](https://www.cbsl.gov.lk/)")
        st.markdown("- [Department of Census and Statistics](https://www.statistics.gov.lk/)")
        st.markdown("- [Board of Investment of Sri Lanka](https://investsrilanka.com/)")
        st.markdown("- [Urban Development Authority](https://www.uda.gov.lk/)")
        st.markdown("- [Colombo Stock Exchange](https://www.cse.lk/)")
        st.markdown("- [IMF — Sri Lanka](https://www.imf.org/en/Countries/LKA)")
        st.markdown("- [World Bank — Sri Lanka](https://www.worldbank.org/en/country/srilanka)")
        st.markdown("- [India–Sri Lanka bilateral relations](https://www.hcicolombo.gov.in/page.php?id=india-sri-lanka-bilateral-relations)")
    with st.form("ai_research_form"):
        research_question = st.text_area(
            "Your research question",
            placeholder="Example: Using the latest official reports, assess the opportunities and risks for Sri Lanka's real-estate and logistics markets from deeper India–Sri Lanka energy and connectivity cooperation. Separate confirmed projects from proposals and cite sources.",
            height=130,
        )
        submitted = st.form_submit_button("Search reports & analyse", type="primary", use_container_width=True)
    if submitted:
        if not research_question.strip():
            st.warning("Enter a question so the research assistant knows what to investigate.")
        else:
            secret_key = None
            try:
                secret_key = st.secrets.get("OPENAI_API_KEY")
            except Exception:
                secret_key = None
            with st.spinner("Searching public sources and preparing an evidence-led answer…"):
                try:
                    answer = research_with_ai(research_question, api_key=secret_key or os.getenv("OPENAI_API_KEY"))
                    st.session_state["latest_ai_research_question"] = research_question
                    st.session_state["latest_ai_research_answer"] = answer
                except RuntimeError as exc:
                    st.warning(str(exc))
                    st.markdown("**To enable AI search:** add an OpenAI API key as OPENAI_API_KEY in your Streamlit deployment's Secrets settings, or set it as an environment variable when hosting the app. Keep the key private; never paste it into app.py or commit it to GitHub.")
                except Exception as exc:
                    st.error(f"The research request did not complete: {exc}")
                    st.caption("Check the API key, account access and network configuration, then retry.")
    if st.session_state.get("latest_ai_research_answer"):
        st.markdown("---")
        st.subheader("Research results")
        st.markdown(f"**Question:** {st.session_state.get('latest_ai_research_question', '')}")
        st.markdown(st.session_state["latest_ai_research_answer"])
        st.caption("AI-generated research can contain errors. Check linked primary sources before making investment, property, legal or policy decisions.")


st.markdown("---")
st.caption("Sri Lanka Economic Intelligence · Research and educational use · Always verify important claims against the linked primary sources.")
