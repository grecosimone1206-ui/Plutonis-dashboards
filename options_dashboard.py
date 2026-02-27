"""
╔══════════════════════════════════════════════════════════╗
║         PHINANCE - Dashboard Vendita Put  v4.0           ║
║         Auto VIX · IV Rank · Live Timestamps             ║
╚══════════════════════════════════════════════════════════╝
Librerie: pip install streamlit numpy pandas scipy plotly yfinance
Avvio:    streamlit run options_dashboard.py
"""

import numpy as np
import pandas as pd
import scipy.stats as si
import streamlit as st
import plotly.graph_objects as go
from dataclasses import dataclass
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    yf = None

# ─────────────────────────────────────────────────────────
# CONFIGURAZIONE PAGINA
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Phinance | Dashboard Opzioni",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# CSS — LUXURY FINTECH v4.0
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@300;400;500&display=swap');

:root {
  --bg-base:         #080C10;
  --bg-surface:      #0C1219;
  --bg-elevated:     #111923;
  --border-subtle:   rgba(255,255,255,0.06);
  --border-medium:   rgba(255,255,255,0.10);
  --border-strong:   rgba(255,255,255,0.16);
  --text-primary:    #F0F6FF;
  --text-secondary:  #8B9FC0;
  --text-muted:      #4A5F7A;
  --accent-cyan:     #00C2FF;
  --accent-green:    #00E5A0;
  --accent-green-dim:#004030;
  --accent-gold:     #FFB547;
  --accent-gold-dim: #3D2800;
  --accent-red:      #FF5A5A;
  --accent-red-dim:  #3D0A0A;
  --radius-sm:       6px;
  --radius-md:       10px;
  --radius-lg:       16px;
  --shadow-md:       0 4px 16px rgba(0,0,0,0.5);
  --font-body:       'DM Sans', sans-serif;
  --font-mono:       'DM Mono', monospace;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background-color: var(--bg-base) !important;
    color: var(--text-primary);
    font-family: var(--font-body);
}
[data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1.2rem; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    font-family: var(--font-mono) !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--accent-cyan) !important;
    border: 2px solid var(--bg-base) !important;
    box-shadow: 0 0 8px rgba(0,194,255,0.5) !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[data-testid="stSliderTrackFill"] {
    background: var(--accent-cyan) !important;
}
[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 10px 16px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: var(--bg-elevated) !important;
    border-color: var(--accent-cyan) !important;
    color: var(--accent-cyan) !important;
    box-shadow: 0 0 12px rgba(0,194,255,0.15) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border-subtle) !important; margin: 1.2rem 0 !important; }

/* ── TIPOGRAFIA ── */
h1, h2, h3 { font-family: var(--font-body) !important; }
h2 {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    border: none !important;
    margin-bottom: 0.8rem !important;
}
hr { border-color: var(--border-subtle) !important; }

/* ── ANIMAZIONI ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 6px currentColor; opacity: 0.8; }
    50%       { box-shadow: 0 0 14px currentColor; opacity: 1; }
}

/* ── HEADER ── */
.ph-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.8rem 0 1.4rem 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 1.6rem;
    animation: fadeSlideUp 0.5s ease both;
}
.ph-logo {
    font-family: var(--font-body);
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    background: linear-gradient(120deg, #FFFFFF 0%, var(--accent-cyan) 60%, #0088CC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.ph-subtitle {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-left: 0.6rem;
}
.ph-tag {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 4px 12px;
}

/* ── BARRA DATI LIVE ── */
.live-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border-subtle);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    overflow: hidden;
    margin-bottom: 1.2rem;
    animation: fadeSlideUp 0.5s 0.05s ease both;
}
.live-cell {
    background: var(--bg-surface);
    padding: 1rem 1.3rem;
    position: relative;
    transition: background 0.2s ease;
}
.live-cell:hover { background: var(--bg-elevated); }

.live-cell-label {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.live-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--accent-green);
    display: inline-block;
    animation: pulseGlow 2s infinite;
    color: var(--accent-green);
}
.live-cell-value {
    font-family: var(--font-body);
    font-size: 1.35rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.3rem;
}
.live-cell-value.cyan  { color: var(--accent-cyan); }
.live-cell-value.green { color: var(--accent-green); }
.live-cell-value.gold  { color: var(--accent-gold); }
.live-cell-value.red   { color: var(--accent-red); }

.live-cell-sub {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--text-muted);
}
.live-cell-change-up   { color: var(--accent-green); font-size: 0.72rem; font-family: var(--font-mono); }
.live-cell-change-down { color: var(--accent-red);   font-size: 0.72rem; font-family: var(--font-mono); }

/* Tooltip "?" aggiornamento */
.info-tooltip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 14px; height: 14px;
    border-radius: 50%;
    border: 1px solid var(--border-medium);
    font-family: var(--font-mono);
    font-size: 0.55rem;
    color: var(--text-muted);
    cursor: help;
    position: relative;
    margin-left: 0.2rem;
    flex-shrink: 0;
}
.info-tooltip:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); }
.info-tooltip .tooltip-content {
    display: none;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-elevated);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-sm);
    padding: 8px 12px;
    white-space: nowrap;
    font-size: 0.65rem;
    color: var(--text-secondary);
    z-index: 100;
    pointer-events: none;
    box-shadow: var(--shadow-md);
    min-width: 200px;
    text-align: left;
    line-height: 1.6;
}
.info-tooltip .tooltip-content::after {
    content: '';
    position: absolute;
    top: 100%; left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: var(--border-medium);
}
.info-tooltip:hover .tooltip-content { display: block; }

/* IV Rank badge */
.ivr-badge {
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 0.58rem;
    letter-spacing: 0.08em;
    padding: 2px 7px;
    border-radius: 4px;
    margin-top: 0.3rem;
}
.ivr-badge.alto   { background: rgba(0,229,160,0.1);  color: var(--accent-green); border: 1px solid rgba(0,229,160,0.2); }
.ivr-badge.medio  { background: rgba(255,181,71,0.1);  color: var(--accent-gold);  border: 1px solid rgba(255,181,71,0.2); }
.ivr-badge.basso  { background: rgba(255,90,90,0.1);   color: var(--accent-red);   border: 1px solid rgba(255,90,90,0.2); }

/* ── SIGNAL BANNER ── */
.signal-banner {
    display: flex;
    align-items: center;
    gap: 1rem;
    border-radius: var(--radius-md);
    padding: 0.9rem 1.4rem;
    margin-bottom: 1.6rem;
    border: 1px solid;
    animation: fadeSlideUp 0.5s 0.1s ease both;
}
.signal-banner.verde  { background: rgba(0,229,160,0.05);  border-color: rgba(0,229,160,0.2); }
.signal-banner.giallo { background: rgba(255,181,71,0.05);  border-color: rgba(255,181,71,0.2); }
.signal-banner.rosso  { background: rgba(255,90,90,0.05);   border-color: rgba(255,90,90,0.2); }
.signal-dot {
    width: 9px; height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
}
.signal-dot.verde  { background: var(--accent-green); box-shadow: 0 0 0 3px rgba(0,229,160,0.15); animation: pulseGlow 2s infinite; color: var(--accent-green); }
.signal-dot.giallo { background: var(--accent-gold);  box-shadow: 0 0 0 3px rgba(255,181,71,0.15); }
.signal-dot.rosso  { background: var(--accent-red);   box-shadow: 0 0 0 3px rgba(255,90,90,0.15); }
.signal-label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    white-space: nowrap;
}
.signal-banner.verde  .signal-label { color: var(--accent-green); }
.signal-banner.giallo .signal-label { color: var(--accent-gold); }
.signal-banner.rosso  .signal-label { color: var(--accent-red); }
.signal-text { font-family: var(--font-body); font-size: 0.85rem; color: var(--text-secondary); }

/* ── KPI CARDS ── */
.kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
    animation: fadeSlideUp 0.5s ease both;
    height: 100%;
}
.kpi-card:hover { border-color: var(--border-medium); transform: translateY(-2px); box-shadow: var(--shadow-md); }
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
.kpi-card:hover::after { opacity: 0.5; }
.kpi-eyebrow {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
}
.kpi-value {
    font-family: var(--font-body);
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.5rem;
}
.kpi-value.cyan  { color: var(--accent-cyan); }
.kpi-value.green { color: var(--accent-green); }
.kpi-value.gold  { color: var(--accent-gold); }
.kpi-value.red   { color: var(--accent-red); }
.kpi-sub { font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-muted); line-height: 1.5; }
.kpi-badge {
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 20px;
    margin-top: 0.5rem;
}
.kpi-badge.green { background: var(--accent-green-dim); color: var(--accent-green); border: 1px solid rgba(0,229,160,0.2); }
.kpi-badge.gold  { background: var(--accent-gold-dim);  color: var(--accent-gold);  border: 1px solid rgba(255,181,71,0.2); }
.kpi-badge.red   { background: var(--accent-red-dim);   color: var(--accent-red);   border: 1px solid rgba(255,90,90,0.2); }

/* ── PANELS ── */
.panel {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    animation: fadeSlideUp 0.5s 0.2s ease both;
    height: 100%;
}
.panel-title {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 1.1rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--border-subtle);
}
.panel-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid var(--border-subtle);
    transition: background 0.15s;
}
.panel-row:last-child { border-bottom: none; }
.panel-row:hover { background: rgba(255,255,255,0.02); margin: 0 -0.5rem; padding: 0.55rem 0.5rem; border-radius: 4px; }
.panel-key { font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-muted); }
.panel-val { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-secondary); font-weight: 500; text-align: right; }
.panel-val.cyan  { color: var(--accent-cyan); }
.panel-val.green { color: var(--accent-green); }
.panel-val.red   { color: var(--accent-red); }
.panel-val.big   { font-size: 1.1rem; color: var(--text-primary); }

/* ── CRISIS PANEL ── */
.crisis-panel {
    background: rgba(255,90,90,0.03);
    border: 1px solid rgba(255,90,90,0.14);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    animation: fadeSlideUp 0.5s 0.2s ease both;
    height: 100%;
}
.crisis-header {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(255,90,90,0.55);
    margin-bottom: 1.1rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(255,90,90,0.1);
}
.crisis-row { display: flex; justify-content: space-between; align-items: center; padding: 0.55rem 0; border-bottom: 1px solid rgba(255,90,90,0.07); }
.crisis-row:last-child { border-bottom: none; }
.crisis-key { font-family: var(--font-mono); font-size: 0.7rem; color: rgba(255,90,90,0.45); }
.crisis-val { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-secondary); font-weight: 500; }
.crisis-val.red   { color: var(--accent-red); }
.crisis-val.green { color: var(--accent-green); }
.crisis-impact {
    margin-top: 1rem;
    padding: 0.8rem 1rem;
    background: rgba(255,90,90,0.05);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(255,90,90,0.1);
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: rgba(255,90,90,0.55);
    text-align: center;
}

/* ── SECTION LABEL ── */
.section-label {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.8rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--border-subtle); }

/* ── SIDEBAR SECTION HEADERS ── */
.sb-section {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 0.8rem 0 0.4rem 0;
    margin-top: 0.3rem;
    border-top: 1px solid var(--border-subtle);
}
.sb-section:first-child { border-top: none; margin-top: 0; }

/* VIX auto badge in sidebar */
.vix-auto-badge {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.08em;
    color: var(--accent-green);
    background: rgba(0,229,160,0.08);
    border: 1px solid rgba(0,229,160,0.15);
    border-radius: 4px;
    padding: 3px 8px;
    display: inline-block;
    margin-top: 0.3rem;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-elevated) !important;
    color: var(--text-muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-medium) !important;
}
[data-testid="stDataFrame"] td {
    background: var(--bg-surface) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
    border-bottom: 1px solid var(--border-subtle) !important;
}

/* ── FOOTER ── */
.ph-footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-top: 1px solid var(--border-subtle);
    margin-top: 2.5rem;
    font-family: var(--font-mono);
    font-size: 0.62rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    line-height: 2;
}

/* ── METRIC CARDS NATIVE (live bar) ── */
.live-bar-wrap [data-testid="stMetric"] {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1rem 1.3rem;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.live-bar-wrap [data-testid="stMetric"]:hover {
    border-color: var(--border-medium);
    transform: translateY(-1px);
}
.live-bar-wrap [data-testid="stMetricLabel"] {
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
.live-bar-wrap [data-testid="stMetricValue"] {
    font-family: var(--font-body) !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: var(--accent-cyan) !important;
    letter-spacing: -0.02em !important;
}
.live-bar-wrap [data-testid="stMetricDelta"] {
    font-family: var(--font-mono) !important;
    font-size: 0.68rem !important;
}
.live-bar-wrap [data-testid="stMetricLabel"] svg {
    color: var(--text-muted) !important;
    transition: color 0.2s ease;
}
.live-bar-wrap [data-testid="stMetricLabel"]:hover svg {
    color: var(--accent-cyan) !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FUNZIONI DATI — yfinance + VIX + IV Rank
# ═══════════════════════════════════════════════════════════

TICKER_DISPONIBILI = {
    "S&P 500 (SPY)":                 "SPY",
    "S&P 500 Indice (^GSPC)":        "^GSPC",
    "NASDAQ 100 (QQQ)":              "QQQ",
    "Dow Jones (^DJI)":              "^DJI",
    "Apple (AAPL)":                  "AAPL",
    "Tesla (TSLA)":                  "TSLA",
    "Nvidia (NVDA)":                 "NVDA",
    "Microsoft (MSFT)":              "MSFT",
    "Amazon (AMZN)":                 "AMZN",
    "Altro (inserisci manualmente)": "MANUALE",
}

def ora_adesso() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

@st.cache_data(ttl=300)
def recupera_dati_mercato(ticker: str) -> dict:
    """
    Recupera da Yahoo Finance:
    - Prezzo Spot + variazione %
    - Volatilità Storica 30gg annualizzata
    - IV Rank (calcolato su 252 giorni di vol. storica rolling)
    - VIX corrente (scaricato in automatico)
    Ogni dato registra il proprio timestamp di aggiornamento.
    """
    ts = ora_adesso()
    try:
        # ── Dati sottostante ──
        s = yf.Ticker(ticker)
        h = s.history(period="1y")          # 1 anno per IV Rank
        if h.empty:
            return {"errore": f"Nessun dato trovato per '{ticker}'"}

        spot = float(h["Close"].iloc[-1])
        var  = ((spot - float(h["Close"].iloc[-2])) / float(h["Close"].iloc[-2]) * 100) if len(h) >= 2 else 0.0

        # Volatilità storica 30gg annualizzata
        ret     = np.log(h["Close"] / h["Close"].shift(1)).dropna()
        vol_30  = float(ret.tail(30).std() * np.sqrt(252) * 100)

        # ── IV Rank ──
        # Calcoliamo la vol. storica rolling 30gg su tutto l'anno
        # IV Rank = (vol oggi - vol min 1Y) / (vol max - vol min) * 100
        vol_rolling = ret.rolling(30).std() * np.sqrt(252) * 100
        vol_rolling = vol_rolling.dropna()
        if len(vol_rolling) >= 10:
            v_min = float(vol_rolling.min())
            v_max = float(vol_rolling.max())
            v_now = float(vol_rolling.iloc[-1])
            iv_rank = round((v_now - v_min) / (v_max - v_min) * 100, 1) if v_max > v_min else 50.0
        else:
            iv_rank = 50.0

        ts_spot = ts
        ts_vol  = ts

        # ── VIX automatico ──
        try:
            vix_ticker = yf.Ticker("^VIX")
            vix_h      = vix_ticker.history(period="5d")
            vix_val    = round(float(vix_h["Close"].iloc[-1]), 2) if not vix_h.empty else None
            ts_vix     = ts
        except Exception:
            vix_val = None
            ts_vix  = "Non disponibile"

        # Nome esteso
        try:
            nome = s.info.get("longName", ticker)
        except Exception:
            nome = ticker

        return {
            "prezzo_spot":  round(spot, 2),
            "variazione_gg":round(var, 2),
            "vol_storica":  round(vol_30, 2),
            "iv_rank":      iv_rank,
            "vix":          vix_val,
            "nome":         nome,
            "ultimo_agg":   h.index[-1].strftime("%d/%m/%Y"),
            "ts_spot":      ts_spot,
            "ts_vol":       ts_vol,
            "ts_vix":       ts_vix,
            "ts_ivrank":    ts,
            "errore":       None,
        }
    except Exception as e:
        return {"errore": str(e)}


# ═══════════════════════════════════════════════════════════
# MOTORE BLACK-SCHOLES
# ═══════════════════════════════════════════════════════════

@dataclass
class Par:
    S: float; K: float; T: float; r: float; sigma: float

def d1d2(p: Par):
    if p.T <= 0 or p.sigma <= 0: return 0.0, 0.0
    d1 = (np.log(p.S/p.K) + (p.r + 0.5*p.sigma**2)*p.T) / (p.sigma*np.sqrt(p.T))
    return d1, d1 - p.sigma*np.sqrt(p.T)

def prezzo_put(p: Par) -> float:
    d1, d2 = d1d2(p)
    return max(p.K*np.exp(-p.r*p.T)*si.norm.cdf(-d2) - p.S*si.norm.cdf(-d1), 0.0)

def prob_ok(p: Par) -> float:
    _, d2 = d1d2(p); return si.norm.cdf(d2)

def calc_greche(p: Par) -> dict:
    if p.T <= 0: return dict(delta=0, gamma=0, theta=0, vega=0, rho=0)
    d1, d2 = d1d2(p); f = si.norm.pdf(d1)
    return {
        "delta": round(-si.norm.cdf(-d1), 4),
        "gamma": round(f/(p.S*p.sigma*np.sqrt(p.T)), 6),
        "theta": round((-(p.S*f*p.sigma)/(2*np.sqrt(p.T)) + p.r*p.K*np.exp(-p.r*p.T)*si.norm.cdf(-d2))/365, 4),
        "vega":  round(p.S*f*np.sqrt(p.T)/100, 4),
        "rho":   round(-p.K*p.T*np.exp(-p.r*p.T)*si.norm.cdf(-d2)/100, 4),
    }

def calc_semaforo(iv, vol, ivr):
    """Usa sia IV vs Vol.Storica che IV Rank per segnale più preciso."""
    ratio = iv/vol if vol > 0 else 1.0
    # Verde se entrambi i segnali sono positivi
    if ratio >= 1.20 and ivr >= 50:
        return {"c":"verde",  "l":"Condizioni Ottime",      "d":f"IV {iv:.1f}% è {ratio:.0%} della vol. storica · IV Rank {ivr:.0f}/100 — premi gonfiati, ottimo per vendere"}
    if ratio >= 1.20 or ivr >= 50:
        return {"c":"giallo", "l":"Condizioni Parzialmente Favorevoli", "d":f"IV {iv:.1f}% · IV Rank {ivr:.0f}/100 — un segnale positivo, l'altro neutro. Valutare con attenzione"}
    if ratio >= 0.85:
        return {"c":"giallo", "l":"Condizioni nella Norma",  "d":f"IV {iv:.1f}% in linea con la storia · IV Rank {ivr:.0f}/100 — valutare il premio"}
    return          {"c":"rosso",  "l":"Condizioni Sfavorevoli",  "d":f"IV {iv:.1f}% bassa · IV Rank {ivr:.0f}/100 — premi insufficienti, meglio aspettare"}

def strike_target(S, sigma, T, r, pt):
    if T <= 0 or sigma <= 0: return S
    return round(S*np.exp((r-0.5*sigma**2)*T + sigma*np.sqrt(T)*si.norm.ppf(1.0-pt)), 2)

def calc_sizing(cap, K, marg, mult=100):
    mc = K*mult*(marg/100); n = int(cap//mc) if mc > 0 else 0
    return {"n":n, "mc":round(mc,2), "imp":round(n*mc,2), "lib":round(cap-n*mc,2)}

def calc_wcs(S, K, prem, n, crash, mult=100):
    Sc = S*(1-crash/100); lc = max(K-Sc,0)-prem
    return {"Sc":round(Sc,2), "lc":round(lc,2), "lt":round(lc*n*mult,2), "pt":round(prem*n*mult,2), "crash":crash}

def pnl_chart(S, K, prem, n, mult=100):
    px  = np.linspace(S*0.55, S*1.20, 400)
    pnl = np.where(px < K, px-K+prem, prem)*n*mult
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=px, y=np.maximum(pnl,0), fill='tozeroy', fillcolor='rgba(0,229,160,0.07)', line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=px, y=np.minimum(pnl,0), fill='tozeroy', fillcolor='rgba(255,90,90,0.07)',  line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=px, y=pnl, line=dict(color='#00C2FF', width=2), name='P&L',
        hovertemplate='<b>Prezzo:</b> %{x:,.2f}<br><b>P&L:</b> %{y:+,.0f} €<extra></extra>'))
    fig.add_vline(x=K,       line=dict(color='#FFB547', dash='dash', width=1), annotation=dict(text=f"Strike {K:,.0f}",   font=dict(color='#FFB547', size=11)))
    fig.add_vline(x=S,       line=dict(color='rgba(255,255,255,0.2)', dash='dot', width=1), annotation=dict(text=f"Spot {S:,.0f}", font=dict(color='#8B9FC0', size=11)))
    fig.add_vline(x=K-prem,  line=dict(color='#A855F7', dash='dash', width=1), annotation=dict(text=f"Pareggio {K-prem:,.0f}", font=dict(color='#A855F7', size=11)))
    fig.add_hline(y=0,       line=dict(color='rgba(255,255,255,0.08)', width=1))
    fig.update_layout(
        paper_bgcolor='#080C10', plot_bgcolor='#0C1219',
        font=dict(family='DM Mono', size=11, color='#8B9FC0'),
        title=dict(text='Profilo Profitto / Perdita a Scadenza', font=dict(family='DM Sans', size=13, color='#8B9FC0'), x=0, xanchor='left', pad=dict(l=0,b=12)),
        xaxis=dict(title='Prezzo del Sottostante a Scadenza', gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)', tickfont=dict(size=10), title_font=dict(size=11)),
        yaxis=dict(title='Profitto / Perdita (€)',            gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)', tickfont=dict(size=10), title_font=dict(size=11)),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#111923', bordercolor='rgba(255,255,255,0.1)', font=dict(family='DM Mono', size=11, color='#F0F6FF')),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("<div class='sb-section' style='border-top:none;margin-top:0'>Strumento</div>", unsafe_allow_html=True)

    scelta = st.selectbox(
        "Sottostante",
        options=list(TICKER_DISPONIBILI.keys()),
        index=1,
        label_visibility="collapsed",
        help="Seleziona lo strumento. Il VIX viene scaricato in automatico."
    )
    tk = TICKER_DISPONIBILI[scelta]
    if tk == "MANUALE":
        raw = st.text_input("Ticker Yahoo Finance", value="SPY", label_visibility="collapsed")
        tk  = raw.upper().strip()

    aggiorna = st.button("↻  Aggiorna Tutti i Dati")

    st.markdown("<div class='sb-section'>Parametri Opzione</div>", unsafe_allow_html=True)

    dte    = st.slider("Giorni alla Scadenza (DTE)", 1, 365, 45,
        help=f"Giorni calendariali alla scadenza.\nOttimale: 35-49 giorni.\nUltimo aggiornamento: impostato da te manualmente.")
    iv_pct = st.slider("Volatilità Implicita IV (%)", 1.0, 150.0, 20.0, 0.5,
        help="Se hai premuto 'Aggiorna', questo campo viene preimpostato automaticamente con il VIX corrente.\nPuoi modificarlo manualmente per confrontare scenari diversi.")
    r_pct  = st.number_input("Tasso Risk-Free (%)", 0.0, 20.0, 4.5, 0.1,
        help="Rendimento BTP/Treasury 10 anni.\nAggiorna ogni 3 mesi circa.")

    st.markdown("<div class='sb-section'>Gestione del Rischio</div>", unsafe_allow_html=True)
    capitale = st.number_input("Capitale Disponibile (€)", 1_000.0, 10_000_000.0, 50_000.0, 1_000.0)
    marg_pct = st.slider("Margine Broker (%)", 5.0, 50.0, 15.0, 1.0,
        help="% dello strike bloccata come garanzia dal broker.\nVerifica nelle impostazioni del tuo broker.")
    crash    = st.slider("Scenario di Crisi (%)", 5.0, 50.0, 20.0, 1.0,
        help="Crollo ipotetico usato per calcolare il worst case scenario.")

    st.markdown("<div class='sb-section'>Obiettivo Strategia</div>", unsafe_allow_html=True)
    prob_t = st.slider("Probabilità di Successo (%)", 70.0, 99.0, 84.0, 1.0,
        help="84% = Delta 0.16 — punto ottimale Tastytrade.\n90% = Delta 0.10 — più conservativo.\n80% = Delta 0.20 — più aggressivo.")


# ═══════════════════════════════════════════════════════════
# RECUPERO DATI
# ═══════════════════════════════════════════════════════════

if ("dati" not in st.session_state or aggiorna or
        st.session_state.get("tk") != tk):
    with st.spinner(f"⟳  Recupero dati per {tk} e VIX…"):
        st.session_state.dati = recupera_dati_mercato(tk)
        st.session_state.tk   = tk

dati = st.session_state.dati
if dati.get("errore"):
    st.error(f"**Errore dati:** {dati['errore']}")
    st.info("💡 Prova con: SPY · QQQ · AAPL · TSLA · MSFT · ^GSPC")
    st.stop()

spot    = dati["prezzo_spot"]
vol_st  = dati["vol_storica"]
iv_rank = dati["iv_rank"]
vix_val = dati["vix"]
var     = dati["variazione_gg"]
nome    = dati["nome"]
agg     = dati["ultimo_agg"]
ts_spot = dati["ts_spot"]
ts_vol  = dati["ts_vol"]
ts_vix  = dati["ts_vix"]
ts_ivr  = dati["ts_ivrank"]

# Preimposta IV con VIX se disponibile e se l'utente ha appena aggiornato
if aggiorna and vix_val is not None:
    iv_pct = vix_val


# ═══════════════════════════════════════════════════════════
# CALCOLI
# ═══════════════════════════════════════════════════════════

T     = dte / 365.0
sigma = iv_pct / 100.0
r     = r_pct / 100.0
K     = strike_target(spot, sigma, T, r, prob_t/100.0)
par   = Par(S=spot, K=K, T=T, r=r, sigma=sigma)
prem  = prezzo_put(par)
prob  = prob_ok(par)
gre   = calc_greche(par)
sema  = calc_semaforo(iv_pct, vol_st, iv_rank)
sz    = calc_sizing(capitale, K, marg_pct)
sc    = calc_wcs(spot, K, prem, sz["n"], crash)
dist  = (spot - K) / spot * 100
ptot  = prem * sz["n"] * 100
thday = abs(gre["theta"]) * sz["n"] * 100
rend  = (ptot / sz["imp"] * 100) if sz["imp"] > 0 else 0

# IV Rank badge
ivr_cls   = "alto" if iv_rank >= 60 else "medio" if iv_rank >= 35 else "basso"
ivr_label = "Alto — Vendi" if iv_rank >= 60 else "Medio — Valuta" if iv_rank >= 35 else "Basso — Aspetta"

# VIX colore
vix_str = f"{vix_val:.1f}" if vix_val else "N/D"
vix_cls = "green" if vix_val and vix_val >= 20 else "gold" if vix_val and vix_val >= 15 else "red"


# ═══════════════════════════════════════════════════════════
# RENDER UI
# ═══════════════════════════════════════════════════════════

# ── HEADER ──
st.markdown(f"""
<div class="ph-header">
    <div style="display:flex;align-items:baseline;gap:0.6rem">
        <span class="ph-logo">Phinance</span>
        <span class="ph-subtitle">Dashboard Vendita Put</span>
    </div>
    <span class="ph-tag">Black-Scholes · Yahoo Finance · v4.0</span>
</div>
""", unsafe_allow_html=True)

# ── BARRA 4 DATI LIVE — colonne native Streamlit con tooltip help ──
fr   = "▲" if var >= 0 else "▼"
sign = "+" if var >= 0 else ""

st.markdown("<div class='live-bar-wrap'>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns(4, gap="small")

with b1:
    st.metric(
        label="● Prezzo Spot",
        value=f"{spot:,.2f}",
        delta=f"{sign}{var:.2f}% oggi",
        help=(
            "PREZZO SPOT\n\n"
            "Prezzo attuale del sottostante scaricato in tempo reale da Yahoo Finance.\n\n"
            f"Fonte: Yahoo Finance (chiusura)\n"
            f"Aggiornato: {ts_spot}"
        )
    )

with b2:
    st.metric(
        label="● Vol. Storica 30gg",
        value=f"{vol_st:.1f}%",
        delta="Volatilità realizzata annualizzata",
        delta_color="off",
        help=(
            "VOLATILITÀ STORICA 30gg\n\n"
            "Quanto si è mosso davvero il mercato negli ultimi 30 giorni.\n"
            "Calcolata su rendimenti logaritmici giornalieri annualizzati (×√252).\n\n"
            f"Fonte: Yahoo Finance (storico prezzi)\n"
            f"Aggiornato: {ts_vol}"
        )
    )

with b3:
    ivr_delta = f"{ivr_label}"
    st.metric(
        label="● IV Rank",
        value=f"{iv_rank:.0f} / 100",
        delta=ivr_delta,
        delta_color="normal" if iv_rank >= 60 else "off",
        help=(
            "IV RANK (0 – 100)\n\n"
            "Dove si trova la volatilità attuale rispetto al suo range degli ultimi 12 mesi.\n\n"
            "  100 = al massimo storico dell'anno → ottimo per vendere\n"
            "   50 = a metà del range → accettabile\n"
            "    0 = al minimo storico dell'anno → evitare\n\n"
            "Regola pratica: operare solo con IV Rank > 50\n\n"
            f"Fonte: Calcolato su dati Yahoo Finance\n"
            f"Aggiornato: {ts_ivr}"
        )
    )

with b4:
    vix_delta = "Preimpostato in IV ✓" if vix_val else "Non disponibile"
    st.metric(
        label="● VIX — Indice di Paura",
        value=vix_str,
        delta=vix_delta,
        delta_color="off",
        help=(
            "VIX — CBOE VOLATILITY INDEX\n\n"
            "Misura la volatilità implicita attesa sull'S&P 500 nei prossimi 30 giorni.\n"
            "Viene scaricato in automatico e preimpostato nel campo IV della sidebar.\n\n"
            "  VIX < 15  → basso, premi scarsi\n"
            "  VIX 15-20 → nella norma\n"
            "  VIX > 20  → elevato, buono per vendere\n"
            "  VIX > 30  → paura, ottimo per vendere\n\n"
            f"Fonte: Yahoo Finance (^VIX)\n"
            f"Aggiornato: {ts_vix}"
        )
    )
st.markdown("</div>", unsafe_allow_html=True)

# ── SIGNAL BANNER ──
st.markdown(f"""
<div class="signal-banner {sema['c']}">
    <span class="signal-dot {sema['c']}"></span>
    <span class="signal-label">{sema['l']}</span>
    <span class="signal-text">{sema['d']}</span>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ──
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(f"""
    <div class="kpi-card" style="animation-delay:0.0s">
        <div class="kpi-eyebrow">🎯 Strike Consigliato</div>
        <div class="kpi-value cyan">{K:,.1f}</div>
        <div class="kpi-sub">{dist:.1f}% sotto il prezzo attuale</div>
        <div><span class="kpi-badge green">OTM TARGET</span></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    bc = "green" if prob >= 0.90 else "gold" if prob >= 0.80 else "red"
    bt = "Eccellente" if prob >= 0.90 else "Accettabile" if prob >= 0.80 else "Rischiosa"
    vc = "green"  if prob >= 0.90 else "gold" if prob >= 0.80 else "red"
    st.markdown(f"""
    <div class="kpi-card" style="animation-delay:0.06s">
        <div class="kpi-eyebrow">✦ Probabilità di Successo</div>
        <div class="kpi-value {vc}">{prob*100:.1f}%</div>
        <div class="kpi-sub">Probabilità che scada senza perdite</div>
        <div><span class="kpi-badge {bc}">{bt}</span></div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card" style="animation-delay:0.12s">
        <div class="kpi-eyebrow">◈ Premio Incassato</div>
        <div class="kpi-value">{prem:.2f}</div>
        <div class="kpi-sub">{sz['n']} contratti → <strong style="color:#00E5A0">+{ptot:,.0f} €</strong> al mese</div>
        <div><span class="kpi-badge green">+{rend:.1f}% / mese sul margine</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.6rem'></div>", unsafe_allow_html=True)

# ── GRAFICO ──
st.plotly_chart(pnl_chart(spot, K, prem, sz["n"]), use_container_width=True)
st.markdown("<div style='margin-top:0.4rem'></div>", unsafe_allow_html=True)

# ── PANNELLI INFERIORI ──
g1, g2, g3 = st.columns(3, gap="medium")

with g1:
    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">Lettere Greche</div>
        <div class="panel-row"><span class="panel-key">Δ Delta (prob. ITM)</span><span class="panel-val cyan">{gre['delta']:.4f} · {abs(gre['delta'])*100:.1f}%</span></div>
        <div class="panel-row"><span class="panel-key">Γ Gamma (accelerazione)</span><span class="panel-val">{gre['gamma']:.6f}</span></div>
        <div class="panel-row"><span class="panel-key">Θ Theta (guadagno/giorno)</span><span class="panel-val green">+{abs(gre['theta']):.4f} €</span></div>
        <div class="panel-row"><span class="panel-key">ν Vega (sensib. IV)</span><span class="panel-val">{gre['vega']:.4f} / 1% IV</span></div>
        <div class="panel-row"><span class="panel-key">ρ Rho (sensib. tassi)</span><span class="panel-val">{gre['rho']:.4f}</span></div>
    </div>
    """, unsafe_allow_html=True)

with g2:
    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">Dimensione Posizione</div>
        <div class="panel-row"><span class="panel-key">Contratti massimi</span><span class="panel-val big cyan">{sz['n']}</span></div>
        <div class="panel-row"><span class="panel-key">Margine per contratto</span><span class="panel-val">{sz['mc']:,.0f} €</span></div>
        <div class="panel-row"><span class="panel-key">Capitale bloccato</span><span class="panel-val">{sz['imp']:,.0f} €</span></div>
        <div class="panel-row"><span class="panel-key">Capitale libero</span><span class="panel-val green">{sz['lib']:,.0f} €</span></div>
        <div class="panel-row"><span class="panel-key">Theta totale / giorno</span><span class="panel-val green">+{thday:,.0f} €</span></div>
        <div class="panel-row"><span class="panel-key">Rendimento mensile</span><span class="panel-val green">{rend:.1f}%</span></div>
    </div>
    """, unsafe_allow_html=True)

with g3:
    pn = sc["lt"] + sc["pt"]
    imp = (pn / capitale * 100) if capitale > 0 else 0
    st.markdown(f"""
    <div class="crisis-panel">
        <div class="crisis-header">⚠ Scenario di Crisi — Crollo {sc['crash']:.0f}%</div>
        <div class="crisis-row"><span class="crisis-key">Prezzo dopo il crollo</span><span class="crisis-val">{sc['Sc']:,.2f}</span></div>
        <div class="crisis-row"><span class="crisis-key">Perdita per contratto</span><span class="crisis-val red">{sc['lc']:,.0f} €</span></div>
        <div class="crisis-row"><span class="crisis-key">Perdita lorda totale</span><span class="crisis-val red">{sc['lt']:,.0f} €</span></div>
        <div class="crisis-row"><span class="crisis-key">Premi già incassati</span><span class="crisis-val green">+{sc['pt']:,.0f} €</span></div>
        <div class="crisis-row"><span class="crisis-key">Perdita netta finale</span><span class="crisis-val red" style="font-size:0.9rem;font-weight:600">{pn:,.0f} €</span></div>
        <div class="crisis-impact">Impatto sul capitale totale: {imp:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ── RIEPILOGO ──
st.markdown("<div class='section-label'>Riepilogo Operazione</div>", unsafe_allow_html=True)
st.dataframe(pd.DataFrame({
    "Parametro": ["Strumento","Prezzo Attuale","Strike Consigliato","Distanza Strike",
                  "Giorni alla Scadenza","IV Impostata","Vol. Storica 30gg","VIX Corrente","IV Rank",
                  "Premio per Contratto","Numero Contratti","Incasso Totale",
                  "Punto di Pareggio","Theta Giornaliero","Rendimento Mensile"],
    "Valore":    [nome, f"{spot:,.2f}", f"{K:,.2f}", f"{dist:.1f}% sotto lo spot",
                  f"{dte} gg", f"{iv_pct:.1f}%", f"{vol_st:.1f}%",
                  f"{vix_str}" + (" (preimpostato in IV)" if vix_val else ""),
                  f"{iv_rank:.0f}/100 — {ivr_label}",
                  f"{prem:.4f}  ({prem*100:.2f} € / contratto 100 azioni)",
                  str(sz["n"]), f"+{ptot:,.0f} €",
                  f"{K-prem:,.2f}", f"+{thday:,.0f} € / giorno",
                  f"{rend:.1f}%  ({rend*12:.1f}% annuo stimato)"],
}), use_container_width=True, hide_index=True,
    column_config={
        "Parametro": st.column_config.TextColumn(width="medium"),
        "Valore":    st.column_config.TextColumn(width="large"),
    })

# ── FOOTER ──
st.markdown("""
<div class="ph-footer">
    Phinance · Sistemi Quantitativi per il Trading di Opzioni<br>
    Solo a scopo educativo · Non costituisce consulenza finanziaria<br>
    Dati: Yahoo Finance · VIX: CBOE via Yahoo Finance · Motore: Black-Scholes v4.0
</div>
""", unsafe_allow_html=True)
