"""Streamlit application for the Fulfillment Reliability Control Tower."""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from config.config import MODELS_DIR, PROCESSED_DATA_DIR  # noqa: E402
from src.risk import classify_risk  # noqa: E402

st.set_page_config(
    page_title="Service Recovery Intelligence",
    page_icon="F",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --navy: #243b64;
        --blue: #3b5ccc;
        --teal: #168f8a;
        --ink: #263653;
        --muted: #687995;
        --panel: #f3f6fc;
        --border: #d7e0ef;
    }
    [data-testid="stSidebar"] {
        background: #eef3fb;
        border-right: 1px solid var(--border);
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #f3f6fc;
    }
    [data-testid="stHeader"] {
        background: #f3f6fc;
    }
    [data-testid="stMainBlockContainer"] {
        max-width: 1440px;
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        padding-bottom: 3rem;
    }
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] label {
        color: var(--ink);
    }
    [data-testid="stSidebar"] * {
        color: var(--ink);
    }
    [data-testid="stSidebar"] .stButton > button {
        border: 1px solid transparent;
        border-radius: 6px;
        min-height: 2.4rem;
        text-align: left;
        padding-left: .75rem;
        font-weight: 600;
        background: transparent;
        transition: background .15s ease, color .15s ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: #bfdbfe;
        background: #eff6ff;
        color: #1d4ed8;
    }
    button[data-testid="stBaseButton-headerNoPadding"] {
        color: #3556a8 !important;
        background: #e7eefb !important;
        border: 1px solid #c5d4ee !important;
        border-radius: 8px !important;
        opacity: 1 !important;
    }
    button[data-testid="stBaseButton-headerNoPadding"]:hover {
        color: #168f8a !important;
        background: #dff4f1 !important;
        border-color: #a9ddd7 !important;
    }
    button[data-testid="stBaseButton-headerNoPadding"] span[data-testid="stIconMaterial"] {
        color: #3556a8 !important;
        opacity: 1 !important;
    }
    button[data-testid="stBaseButton-headerNoPadding"]:hover span[data-testid="stIconMaterial"] {
        color: #168f8a !important;
    }
    button[data-testid="stExpandSidebarButton"] {
        color: #3556a8 !important;
        background: #e7eefb !important;
        border: 1px solid #c5d4ee !important;
        border-radius: 8px !important;
        opacity: 1 !important;
    }
    button[data-testid="stExpandSidebarButton"]:hover {
        color: #168f8a !important;
        background: #dff4f1 !important;
        border-color: #a9ddd7 !important;
    }
    button[data-testid="stExpandSidebarButton"] span[data-testid="stIconMaterial"] {
        color: #3556a8 !important;
        opacity: 1 !important;
    }
    button[data-testid="stExpandSidebarButton"]:hover span[data-testid="stIconMaterial"] {
        color: #168f8a !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] {
        margin-bottom: .35rem;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--border);
    }
    .brand-mark {
        width: 34px;
        height: 34px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        background: #3556a8;
        color: #ffffff !important;
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .04em;
        margin-bottom: .7rem;
    }
    .brand-title {
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: -.01em;
        margin-bottom: .1rem;
    }
    .brand-subtitle {
        color: var(--muted) !important;
        font-size: .76rem;
        line-height: 1.35;
        margin-bottom: 1.35rem;
    }
    .sidebar-section {
        color: #94a3b8 !important;
        font-size: .64rem;
        font-weight: 800;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin: 1rem 0 .45rem;
    }
    .page-kicker {
        display: inline-block;
        color: #168f8a;
        background: #e3f5f2;
        border: 1px solid #bfe5df;
        border-radius: 999px;
        padding: .28rem .62rem;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin: .35rem 0 .7rem;
        line-height: 1.2;
    }
    .executive-note {
        padding: .8rem 1rem;
        background: #e8f7f5;
        border-left: 3px solid #168f8a;
        color: #40536f;
        font-size: .86rem;
        line-height: 1.5;
        margin: .9rem 0 1.25rem;
    }
    .hero-panel {
        position: relative;
        overflow: hidden;
        padding: 1.7rem 2rem;
        background: linear-gradient(120deg, #304a91 0%, #5264bd 58%, #168f8a 145%);
        border-radius: 14px;
        box-shadow: 0 12px 30px rgba(15, 23, 42, .12);
        margin: .75rem 0 1.4rem;
    }
    .hero-panel:after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -80px;
        top: -130px;
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(255,255,255,.04), 0 0 0 56px rgba(255,255,255,.025);
    }
    .hero-panel h1, .hero-panel p {
        color: #ffffff !important;
    }
    .hero-panel h1 {
        font-size: 2.25rem;
        margin: 0 0 .35rem;
        letter-spacing: -.03em;
    }
    .hero-panel p {
        color: #cbd5e1 !important;
        margin: 0;
        max-width: 760px;
        line-height: 1.5;
    }
    .section-label {
        color: #64748b;
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin: 1.5rem 0 .65rem;
    }
    .decision-card {
        min-height: 132px;
        border: 1px solid var(--border);
        border-radius: 8px;
        background: #fbfcff;
        padding: .9rem 1rem;
    }
    .decision-card strong {
        display: block;
        color: #304a72;
        margin-bottom: .35rem;
    }
    .decision-card span {
        color: #64748b;
        font-size: .82rem;
        line-height: 1.4;
    }
    [data-testid="stMetric"] {
        background: #f9fbff;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: .9rem 1rem;
        box-shadow: 0 3px 10px rgba(61, 87, 137, .07);
        min-height: 96px;
    }
    [data-testid="stMetric"]:nth-child(1) {
        background: #e8f1ff;
        border-color: #c9daf8;
    }
    [data-testid="stMetric"]:nth-child(2) {
        background: #e9f8f5;
        border-color: #c8e8e2;
    }
    [data-testid="stMetric"]:nth-child(3) {
        background: #fff4df;
        border-color: #f2dfb6;
    }
    [data-testid="stMetric"]:nth-child(4) {
        background: #f1ecff;
        border-color: #ddd1fa;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
    }
    [data-testid="stMetricValue"] {
        color: #304a72 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #475569 !important;
    }
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [role="combobox"] {
        color: #304a72 !important;
        background: #f8faff !important;
        border-color: #c4d2e8 !important;
        border-radius: 10px 0 0 10px !important;
        min-height: 38px !important;
        font-weight: 600 !important;
        box-shadow: inset 0 1px 2px rgba(48, 74, 114, .04) !important;
    }
    [data-testid="stNumberInput"] div.react-aria-TextField {
        border: 1px solid #c4d2e8 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 6px rgba(61, 87, 137, .05) !important;
    }
    [data-testid="stNumberInput"] div.react-aria-TextField:focus-within {
        border-color: #6f86d7 !important;
        box-shadow: 0 0 0 3px rgba(82, 100, 189, .14) !important;
    }
    [data-testid="stNumberInput"] input:focus {
        outline: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stNumberInput"] > div {
        border-radius: 10px !important;
    }
    [data-testid="stNumberInput"] button[data-testid="stNumberInputStepUp"],
    [data-testid="stNumberInput"] button[data-testid="stNumberInputStepDown"] {
        color: #3556a8 !important;
        background: #e8f0ff !important;
        border: 0 !important;
        border-left: 1px solid #c4d2e8 !important;
        width: 34px !important;
        min-width: 34px !important;
        transition: background .15s ease, color .15s ease !important;
    }
    [data-testid="stNumberInput"] button[data-testid="stNumberInputStepUp"] {
        border-radius: 0 10px 0 0 !important;
        border-bottom: 1px solid #c4d2e8 !important;
    }
    [data-testid="stNumberInput"] button[data-testid="stNumberInputStepDown"] {
        border-radius: 0 0 10px 0 !important;
    }
    [data-testid="stNumberInput"] button[data-testid="stNumberInputStepUp"]:hover,
    [data-testid="stNumberInput"] button[data-testid="stNumberInputStepDown"]:hover {
        color: #168f8a !important;
        background: #d9f3ef !important;
    }
    [data-testid="stNumberInput"]:focus-within input {
        border-color: #6f86d7 !important;
        box-shadow: 0 0 0 3px rgba(82, 100, 189, .14) !important;
    }
    [data-testid="stNumberInput"]:focus-within button {
        border-color: #6f86d7 !important;
    }
    [data-testid="stSelectbox"] [role="combobox"] {
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(61, 87, 137, .05) !important;
    }
    [data-testid="stSelectbox"] button {
        color: #3556a8 !important;
        background: #e8f0ff !important;
        border-color: #c4d2e8 !important;
    }
    [data-testid="stFormSubmitButton"] button {
        color: #ffffff !important;
        background: #4162b5 !important;
        border: 1px solid #4162b5 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        color: #ffffff !important;
        background: #168f8a !important;
        border-color: #168f8a !important;
    }
    [data-testid="stFormSubmitButton"] button p {
        color: #ffffff !important;
    }
    [data-testid="stAlert"] {
        border-radius: 6px;
    }
    [data-testid="stPlotlyChart"] {
        background: #fbfcff;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: .35rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, .03);
    }
    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] {
            padding-left: 1.25rem;
            padding-right: 1.25rem;
        }
    }
    @media (max-width: 600px) {
        [data-testid="stMainBlockContainer"] {
            padding-top: 1rem;
            padding-left: .75rem;
            padding-right: .75rem;
        }
        .hero-panel {
            padding: 1.1rem 1rem;
            border-radius: 10px;
        }
        .hero-panel h1 {
            font-size: 1.55rem;
            line-height: 1.15;
        }
        .hero-panel p {
            font-size: .86rem;
        }
        .decision-card {
            min-height: auto;
            margin-bottom: .65rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_artifacts() -> tuple[dict, dict]:
    return (
        joblib.load(MODELS_DIR / "delivery_delay.joblib"),
        joblib.load(MODELS_DIR / "dissatisfaction.joblib"),
    )


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(PROCESSED_DATA_DIR / "delivery_delay.csv"),
        pd.read_csv(PROCESSED_DATA_DIR / "dissatisfaction.csv"),
    )


def metric_card(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label, value, help=help_text)


try:
    delay_artifact, dissatisfaction_artifact = load_artifacts()
    delay_data, dissatisfaction_data = load_data()
except FileNotFoundError:
    st.error("Model artifacts are missing. Run `python BIa\\scripts\\train_models.py` first.")
    st.stop()

delay_metrics = delay_artifact["metrics"]
dissatisfaction_metrics = dissatisfaction_artifact["metrics"]
PLOTLY_TEMPLATE = "plotly_white"
pages = [
    ("Executive Overview", "Executive Overview"),
    ("Delivery Reliability", "Delivery Risk Prediction"),
    ("Customer Experience", "Customer Dissatisfaction Prediction"),
    ("Orders Needing Attention", "Integrated Risk Analysis"),
    ("Model Governance", "Model Performance"),
]
if "active_page" not in st.session_state:
    st.session_state.active_page = "Executive Overview"

with st.sidebar:
    st.markdown('<div class="brand-mark">SR</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-title">Service Recovery Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="brand-subtitle">Decision support for fulfillment exceptions and customer experience.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-section">Pages</div>', unsafe_allow_html=True)
    for label, destination in pages:
        if st.button(
            label,
            key=f"nav_{destination}",
            type="primary" if st.session_state.active_page == destination else "secondary",
            width="stretch",
        ):
            st.session_state.active_page = destination
            st.rerun()

page = st.session_state.active_page

if page == "Executive Overview":
    st.markdown('<div class="page-kicker">Management brief · service recovery</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-panel"><h1>Service Recovery Intelligence</h1>'
        '<p>A decision-support workspace for finding fulfillment exceptions early, estimating customer impact, '
        'and directing operational attention where it can create the most value.</p></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Orders analysed", f"{len(delay_data):,}")
    with c2:
        metric_card("Observed delay rate", f"{delay_data.is_delayed.mean():.1%}")
    with c3:
        metric_card("Observed dissatisfaction", f"{dissatisfaction_data.is_dissatisfied.mean():.1%}")
    with c4:
        metric_card("Test ROC-AUC (delay)", f"{delay_metrics['test']['roc_auc']:.3f}")
    st.markdown('<div class="section-label">Current operating position</div>', unsafe_allow_html=True)
    chart = pd.DataFrame(
        {"Outcome": ["Delayed", "On time", "Dissatisfied", "Not dissatisfied"],
         "Rate": [delay_data.is_delayed.mean(), 1-delay_data.is_delayed.mean(),
                  dissatisfaction_data.is_dissatisfied.mean(), 1-dissatisfaction_data.is_dissatisfied.mean()]}
    )
    operating_fig = px.bar(
        chart,
        x="Outcome",
        y="Rate",
        color="Outcome",
        text_auto=".1%",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#168f8a", "#9eb8dc", "#e7a83b", "#8d9ab3"],
    )
    operating_fig.update_layout(
        height=330,
        margin=dict(l=12, r=12, t=18, b=12),
        showlegend=False,
        paper_bgcolor="#fbfcff",
        plot_bgcolor="#fbfcff",
        yaxis=dict(tickformat=".0%", title=None, gridcolor="#d7e0ef", tickfont=dict(color="#40536f")),
        xaxis=dict(title=None, showgrid=False, tickfont=dict(color="#40536f")),
        font=dict(color="#304a72"),
    )
    st.plotly_chart(operating_fig, width="stretch", config={"displaylogo": False})
    st.markdown('<div class="section-label">How the system supports decisions</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown('<div class="decision-card"><strong>1 · Detect</strong><span>Surface orders with elevated late-delivery or low-review likelihood before the outcome is confirmed.</span></div>', unsafe_allow_html=True)
    with d2:
        st.markdown('<div class="decision-card"><strong>2 · Prioritise</strong><span>Combine two service signals into a transparent intervention queue instead of treating every order equally.</span></div>', unsafe_allow_html=True)
    with d3:
        st.markdown('<div class="decision-card"><strong>3 · Govern</strong><span>Compare chronological test metrics and keep the distinction between evidence and prediction visible.</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="executive-note"><b>Management interpretation:</b> historical rates describe what has already happened. '
        'Risk scores are prioritisation signals, not guarantees. The recommended operating response is investigation and service recovery—not automatic action.</div>',
        unsafe_allow_html=True,
    )

elif page == "Delivery Risk Prediction":
    st.markdown('<div class="page-kicker">Decision support · service reliability</div>', unsafe_allow_html=True)
    st.title("Delivery Reliability")
    st.caption("Estimate the likelihood that an order will miss its expected delivery commitment.")
    row = delay_data.sample(1, random_state=42).iloc[0]
    with st.form("delivery_form"):
        price = st.number_input("Total item price", min_value=0.0, value=float(row.total_price))
        freight = st.number_input("Total freight value", min_value=0.0, value=float(row.total_freight_value))
        items = st.number_input("Item count", min_value=0, value=int(row.item_count), step=1)
        payment = st.number_input("Payment total", min_value=0.0, value=float(row.payment_value_total))
        states = sorted(delay_data["customer_state"].dropna().astype(str).str.upper().unique())
        state = st.selectbox("Customer state", states, index=states.index(str(row.customer_state).upper()), help="Use the two-letter Brazilian state code.")
        submitted = st.form_submit_button("Assess delivery reliability")
    if submitted:
        if items < 1:
            st.error("Item count must be at least 1.")
            st.stop()
        if not state.strip():
            st.error("Customer state is required.")
            st.stop()
        sample = row.to_frame().T.copy()
        sample["total_price"] = price
        sample["total_freight_value"] = freight
        sample["item_count"] = items
        sample["payment_value_total"] = payment
        sample["customer_state"] = state
        probability = float(delay_artifact["model"].predict_proba(sample[delay_artifact["features"]])[:, 1][0])
        st.metric("Estimated late-delivery likelihood", f"{probability:.1%}")
        st.warning("Use this score to prioritise operational review. It does not confirm that the order will be late.")

elif page == "Customer Dissatisfaction Prediction":
    st.markdown('<div class="page-kicker">Decision support · customer experience</div>', unsafe_allow_html=True)
    st.title("Customer Experience Signals")
    st.caption("Estimate the likelihood that an order may result in a low customer review.")
    row = dissatisfaction_data.sample(1, random_state=7).iloc[0]
    with st.form("dissatisfaction_form"):
        price = st.number_input("Total item price", min_value=0.0, value=float(row.total_price), key="d_price")
        freight = st.number_input("Total freight value", min_value=0.0, value=float(row.total_freight_value), key="d_freight")
        items = st.number_input("Item count", min_value=0, value=int(row.item_count), step=1, key="d_items")
        states = sorted(dissatisfaction_data["customer_state"].dropna().astype(str).str.upper().unique())
        state = st.selectbox("Customer state", states, index=states.index(str(row.customer_state).upper()), key="d_state", help="Use the two-letter Brazilian state code.")
        submitted = st.form_submit_button("Assess experience risk")
    if submitted:
        if items < 1:
            st.error("Item count must be at least 1.")
            st.stop()
        if not state.strip():
            st.error("Customer state is required.")
            st.stop()
        sample = row.to_frame().T.copy()
        sample["total_price"] = price
        sample["total_freight_value"] = freight
        sample["item_count"] = items
        sample["customer_state"] = state
        probability = float(dissatisfaction_artifact["model"].predict_proba(sample[dissatisfaction_artifact["features"]])[:, 1][0])
        st.metric("Estimated low-review likelihood", f"{probability:.1%}")
        st.warning("Use this score to prioritise service recovery. It is not a confirmed customer outcome.")

elif page == "Integrated Risk Analysis":
    st.markdown('<div class="page-kicker">Decision support · operational review</div>', unsafe_allow_html=True)
    st.title("Orders Needing Attention")
    st.caption("A ranked worklist of orders with elevated delivery or customer-experience risk.")
    st.info(
        "This page helps an operations team decide which orders to review first. "
        "Orders are scored for late-delivery likelihood and low-review likelihood, then grouped into clear priority categories. "
        "The list recommends an investigation step; it does not automatically contact customers or change an order."
    )
    n = st.slider("Orders to score", 25, 500, 100)
    sample = delay_data.sample(n, random_state=42).copy()
    delay_prob = delay_artifact["model"].predict_proba(sample[delay_artifact["features"]])[:, 1]
    diss_sample = dissatisfaction_data.set_index("order_id").reindex(sample.order_id).reset_index()
    diss_prob = dissatisfaction_artifact["model"].predict_proba(diss_sample[dissatisfaction_artifact["features"]])[:, 1]
    sample["delay_probability"] = delay_prob
    sample["dissatisfaction_probability"] = diss_prob
    sample["risk_category"] = [classify_risk(a, b) for a, b in zip(delay_prob, diss_prob)]
    action_map = {
        "Highest intervention priority": "Escalate to service recovery owner",
        "Delivery monitoring": "Review carrier and promised-date exposure",
        "Investigate non-delivery causes": "Review payment, seller, and order friction",
        "Normal monitoring": "Continue standard operational monitoring",
    }
    sample["recommended_action"] = sample["risk_category"].map(action_map)
    counts = sample["risk_category"].value_counts().rename_axis("Risk category").reset_index(name="Orders")
    high_priority = int((sample["risk_category"] == "Highest intervention priority").sum())
    st.metric(
        "Orders with two risk signals",
        f"{high_priority:,}",
        help="Orders with both estimated delivery and customer-experience risk at or above the policy threshold.",
    )
    queue_fig = px.bar(
        counts,
        x="Risk category",
        y="Orders",
        color="Risk category",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#168f8a", "#5264bd", "#e7a83b", "#7183a5"],
    )
    queue_fig.update_layout(
        height=340,
        margin=dict(l=12, r=12, t=18, b=12),
        paper_bgcolor="#fbfcff",
        plot_bgcolor="#fbfcff",
        xaxis=dict(title=None, showgrid=False, tickfont=dict(color="#40536f")),
        yaxis=dict(title=None, gridcolor="#d7e0ef", tickfont=dict(color="#40536f")),
        font=dict(color="#304a72"),
        showlegend=False,
    )
    st.plotly_chart(queue_fig, width="stretch", config={"displaylogo": False})
    st.dataframe(
        sample[["order_id", "delay_probability", "dissatisfaction_probability", "risk_category", "recommended_action"]]
        .sort_values(["risk_category", "delay_probability"], ascending=[True, False]),
        width="stretch",
        hide_index=True,
    )

else:
    st.markdown('<div class="page-kicker">Decision support · governance</div>', unsafe_allow_html=True)
    st.title("Model Governance")
    st.caption("Transparent evaluation for responsible operational use.")
    g1, g2 = st.columns(2)
    with g1:
        delay_auc = delay_metrics["test"]["roc_auc"]
        delay_verdict = "Pilot only · improve before automated use" if delay_auc < 0.55 else "Suitable for controlled operational pilot"
        st.metric("Delivery reliability test ROC-AUC", f"{delay_auc:.3f}")
        st.warning(delay_verdict)
    with g2:
        diss_auc = dissatisfaction_metrics["test"]["roc_auc"]
        diss_verdict = "Suitable for controlled operational pilot" if diss_auc >= 0.60 else "Pilot only · improve before operational use"
        st.metric("Customer experience test ROC-AUC", f"{diss_auc:.3f}")
        if diss_auc >= 0.60:
            st.success(diss_verdict)
        else:
            st.warning(diss_verdict)
    rows = []
    for label, metrics in [("Delivery delay", delay_metrics), ("Dissatisfaction", dissatisfaction_metrics)]:
        for split, values in metrics.items():
            rows.append({"Model": label, "Split": split.title(), **{k: values[k] for k in ("accuracy", "precision", "recall", "f1", "roc_auc")}})
    table = pd.DataFrame(rows)
    st.dataframe(table, width="stretch", hide_index=True)
    comparison_rows = []
    for label, artifact in [
        ("Delivery reliability", delay_artifact),
        ("Customer experience", dissatisfaction_artifact),
    ]:
        selection = artifact.get("model_selection", {})
        for candidate, candidate_metrics in selection.get("candidates", {}).items():
            comparison_rows.append(
                {
                    "Model": label,
                    "Candidate": candidate.replace("_", " ").title(),
                    "Validation ROC-AUC": candidate_metrics["validation"]["roc_auc"],
                    "Test ROC-AUC": candidate_metrics["test"]["roc_auc"],
                    "Selected": candidate == selection.get("selected"),
                }
            )
    if comparison_rows:
        st.markdown('<div class="section-label">Model selection evidence</div>', unsafe_allow_html=True)
        st.caption("The winning candidate was selected using validation ROC-AUC before the chronological test set was inspected.")
        st.dataframe(pd.DataFrame(comparison_rows), width="stretch", hide_index=True)
    metric = st.selectbox("Chart metric", ["roc_auc", "f1", "precision", "recall"])
    governance_fig = px.bar(
        table,
        x="Model",
        y=metric,
        color="Split",
        barmode="group",
        text_auto=".3f",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#5264bd", "#168f8a", "#e7a83b"],
    )
    governance_fig.update_layout(
        height=360,
        paper_bgcolor="#fbfcff",
        plot_bgcolor="#fbfcff",
        margin=dict(l=12, r=12, t=18, b=12),
        font=dict(color="#304a72"),
        xaxis=dict(title=None, showgrid=False, tickfont=dict(color="#40536f")),
        yaxis=dict(title=None, gridcolor="#d7e0ef", tickfont=dict(color="#40536f")),
        legend=dict(font=dict(color="#40536f")),
    )
    st.plotly_chart(governance_fig, width="stretch", config={"displaylogo": False})
    st.caption("Metrics are calculated from saved model artifacts using chronological train, validation, and test splits.")
