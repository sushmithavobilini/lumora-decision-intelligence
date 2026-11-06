import streamlit as st
from .config import *

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --lumora-bg: #070b14;
        --lumora-surface: rgba(15, 23, 42, .78);
        --lumora-border: rgba(148, 163, 184, .14);
        --lumora-indigo: #6366f1;
        --lumora-purple: #a855f7;
        --lumora-gold: #f59e0b;
        --lumora-cyan: #06b6d4;
        --lumora-emerald: #10b981;
        --lumora-rose: #f43f5e;
    }

    html, body, [class*="css"], button, input, textarea {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 78% 0%, rgba(99,102,241,.10), transparent 34%),
            radial-gradient(ellipse at 8% 92%, rgba(168,85,247,.06), transparent 30%),
            #070b14;
        color: #e5e7eb;
    }
    [data-testid="stHeader"] {
        background: rgba(7,11,20,.82);
        backdrop-filter: blur(16px);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080d19 0%, #0b1220 100%);
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] > div {
        background: transparent;
    }
    [data-testid="stSidebar"] * {
        color: #dbe3f0;
    }
    [data-testid="stSidebar"] h2 {
        letter-spacing: .12em;
        font-weight: 800;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 5px;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 8px 10px;
        border-radius: 10px;
        transition: background .18s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(99,102,241,.12);
    }
    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: -.025em;
    }
    p, label, .stCaption, [data-testid="stMarkdownContainer"] {
        color: #cbd5e1;
    }

    .lumora-hero {
        background:
            radial-gradient(circle at 88% 12%, rgba(99,102,241,.22), transparent 34%),
            linear-gradient(125deg, rgba(15,23,42,.96), rgba(17,24,39,.86));
        border: 1px solid rgba(129,140,248,.24);
        border-radius: 20px;
        padding: 25px 28px;
        margin: 4px 0 20px;
        box-shadow: 0 18px 50px rgba(0,0,0,.28);
        backdrop-filter: blur(16px);
    }
    .lumora-hero h1 {
        font-size: clamp(25px, 3vw, 34px);
        margin: 5px 0 0;
        color: #fff !important;
        font-weight: 800;
    }
    .lumora-hero p {
        color: #aab7cc;
        margin: 8px 0 0;
        font-size: 13px;
    }
    .eyebrow {
        color: #a5b4fc;
        font-size: 10px;
        letter-spacing: .17em;
        font-weight: 800;
        text-transform: uppercase;
    }

    .kpi-card {
        background: linear-gradient(145deg, rgba(20,29,49,.94), rgba(15,23,42,.82));
        border: 1px solid rgba(148,163,184,.15);
        border-radius: 16px;
        padding: 16px 17px;
        min-height: 112px;
        box-shadow: 0 10px 28px rgba(0,0,0,.18);
        backdrop-filter: blur(16px);
        transition: transform .18s ease, border-color .18s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99,102,241,.42);
    }
    .kpi-label {
        color: #94a3b8;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .09em;
        text-transform: uppercase;
    }
    .kpi-value {
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 26px;
        margin-top: 9px;
        letter-spacing: -.04em;
    }
    .kpi-note {
        color: #718096;
        font-size: 10px;
        margin-top: 4px;
    }
    .panel {
        background: rgba(15,23,42,.78);
        border: 1px solid rgba(148,163,184,.14);
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 12px 30px rgba(0,0,0,.14);
        backdrop-filter: blur(16px);
    }
    .insight {
        background: rgba(6,182,212,.09);
        border: 1px solid rgba(6,182,212,.18);
        border-left: 3px solid #06b6d4;
        padding: 12px 15px;
        border-radius: 10px;
        color: #d8f5fa;
        margin: 8px 0;
    }
    .warning {
        background: rgba(245,158,11,.09);
        border: 1px solid rgba(245,158,11,.20);
        border-left: 3px solid #f59e0b;
        padding: 12px 15px;
        border-radius: 10px;
        color: #fde9c1;
        margin: 8px 0;
    }
    .muted {
        color: #8492a8;
        font-size: 11px;
    }

    div[data-testid="stMetric"] {
        background: rgba(15,23,42,.78);
        border: 1px solid rgba(148,163,184,.15);
        border-radius: 14px;
        padding: 13px 15px;
        box-shadow: 0 8px 22px rgba(0,0,0,.14);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #34d399 !important;
    }

    .stButton button, .stDownloadButton button {
        border-radius: 10px;
        border: 1px solid rgba(129,140,248,.42);
        background: linear-gradient(110deg, #4f46e5, #6366f1);
        color: white;
        font-weight: 700;
        transition: all .18s ease;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        border-color: #a5b4fc;
        background: linear-gradient(110deg, #4338ca, #6366f1);
        color: white;
        box-shadow: 0 6px 18px rgba(99,102,241,.2);
    }
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div {
        background: #111b2d;
        border-color: #334155;
        border-radius: 10px;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid #263449;
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stExpander"] {
        background: rgba(15,23,42,.52);
        border: 1px solid rgba(148,163,184,.14);
        border-radius: 12px;
    }
    [data-testid="stChatMessage"] {
        background: rgba(15,23,42,.66);
        border: 1px solid rgba(148,163,184,.10);
        border-radius: 14px;
    }
    [data-testid="stChatInput"] textarea {
        background: #111b2d;
        border: 1px solid #334155;
        border-radius: 12px;
        color: #f8fafc;
    }
    hr {
        border-color: #1e293b;
    }
    ::selection {
        background: rgba(99,102,241,.35);
    }
    </style>
    """, unsafe_allow_html=True)

def hero(title, subtitle, tag="LUMORA DECISION INTELLIGENCE"):
    st.markdown(f'<div class="lumora-hero"><div class="eyebrow">{tag}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def kpi_card(label, value, note=""):
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

def insight(text, warning=False):
    cls="warning" if warning else "insight"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)
