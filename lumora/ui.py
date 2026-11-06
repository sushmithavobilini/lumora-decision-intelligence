import streamlit as st
from .config import *

def apply_theme():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] {{font-family:'DM Sans',sans-serif;}}
    .stApp {{background:radial-gradient(circle at 80% 0%, #12314b 0%, #091c2d 34%, #071827 75%); color:{TEXT};}}
    [data-testid="stSidebar"] {{background:linear-gradient(180deg,#061321,#0d263b); border-right:1px solid #1b3a52;}}
    [data-testid="stSidebar"] * {{color:#e8f1f8 !important;}}
    [data-testid="stHeader"] {{background:rgba(7,24,39,.7);}}
    h1,h2,h3,h4 {{font-family:'Manrope',sans-serif !important; color:#f4f8fc !important;}}
    p, label, span, div {{ }}
    .lumora-hero {{background:linear-gradient(120deg,#102d46 0%,#16466a 58%,#17617a 100%); border:1px solid #2b5877; border-radius:22px; padding:28px 30px; margin:4px 0 22px; box-shadow:0 18px 45px rgba(0,0,0,.22);}}
    .lumora-hero h1 {{font-size:34px; margin:0; color:#fff !important;}}
    .lumora-hero p {{color:#c8dceb; margin:8px 0 0; font-size:14px;}}
    .eyebrow {{color:#70c7df; font-size:11px; letter-spacing:.16em; font-weight:700; text-transform:uppercase;}}
    .kpi-card {{background:linear-gradient(150deg,#122e45,#0e263b); border:1px solid #23465f; border-radius:17px; padding:17px 18px; min-height:116px; box-shadow:0 8px 24px rgba(0,0,0,.13);}}
    .kpi-label {{color:#a9bfd0; font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase;}}
    .kpi-value {{color:#f4f9fd; font-family:'Manrope'; font-weight:800; font-size:27px; margin-top:9px;}}
    .kpi-note {{color:#82a0b6; font-size:11px; margin-top:3px;}}
    .panel {{background:#0e263b; border:1px solid #23465f; border-radius:17px; padding:18px 20px;}}
    .insight {{background:#102f48; border-left:4px solid #48a6d4; padding:13px 16px; border-radius:9px; color:#dceaf4; margin:8px 0;}}
    .warning {{background:#3a2c1c; border-left:4px solid #e6a64b; padding:13px 16px; border-radius:9px; color:#f8e7c8; margin:8px 0;}}
    .muted {{color:#91a9bc; font-size:12px;}}
    div[data-testid="stMetric"] {{background:#102b41; border:1px solid #244860; border-radius:15px; padding:14px;}}
    div[data-testid="stMetric"] label {{color:#a9bfd0 !important;}}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{color:#f4f9fd !important;}}
    .stButton button, .stDownloadButton button {{border-radius:10px; border:1px solid #3c8fc2; background:linear-gradient(110deg,#17618e,#247db0); color:white; font-weight:700;}}
    .stButton button:hover, .stDownloadButton button:hover {{border-color:#73c8e1; color:white;}}
    [data-testid="stDataFrame"] {{border:1px solid #25445a; border-radius:12px; overflow:hidden;}}
    [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {{background:#102b41; border-color:#2a4b63;}}
    hr {{border-color:#24445b;}}
    </style>
    """, unsafe_allow_html=True)

def hero(title, subtitle, tag="LUMORA DECISION INTELLIGENCE"):
    st.markdown(f'<div class="lumora-hero"><div class="eyebrow">{tag}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def kpi_card(label, value, note=""):
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

def insight(text, warning=False):
    cls="warning" if warning else "insight"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)
