"""
╔══════════════════════════════════════════════════════════╗
║         PHINANCE - Dashboard Vendita Put  v5.1           ║
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
# CSS — inline
# ─────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@300;400;500&display=swap');

/* ── VARIABILI ── */
:root {
  --bg-base:         #060A0E;
  --bg-surface:      #0A1118;
  --bg-elevated:     #0F1822;
  --bg-card:         #0C1520;
  --border-subtle:   rgba(255,255,255,0.055);
  --border-medium:   rgba(255,255,255,0.09);
  --border-strong:   rgba(255,255,255,0.15);
  --text-primary:    #EEF4FF;
  --text-secondary:  #7A90B0;
  --text-muted:      #3E526A;
  --accent-cyan:     #00C2FF;
  --accent-cyan-soft:rgba(0,194,255,0.08);
  --accent-green:    #00E5A0;
  --accent-green-dim:rgba(0,229,160,0.08);
  --accent-gold:     #FFB547;
  --accent-gold-dim: rgba(255,181,71,0.08);
  --accent-red:      #FF5A5A;
  --accent-red-dim:  rgba(255,90,90,0.06);
  --radius-sm:       8px;
  --radius-md:       12px;
  --radius-lg:       18px;
  --radius-xl:       24px;
  --shadow-sm:       0 2px 8px rgba(0,0,0,0.3);
  --shadow-md:       0 4px 20px rgba(0,0,0,0.45);
  --shadow-lg:       0 8px 40px rgba(0,0,0,0.6);
  --shadow-glow-c:   0 0 24px rgba(0,194,255,0.12);
  --font-body:       'DM Sans', sans-serif;
  --font-mono:       'DM Mono', monospace;
}

/* ── RESET ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background-color: var(--bg-base) !important;
    color: var(--text-primary);
    font-family: var(--font-body);
}
[data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }
.block-container { padding: 2.5rem 3rem !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1118 0%, #080E15 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] > div { padding: 2rem 1.4rem; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: rgba(0,194,255,0.4) !important;
    box-shadow: 0 0 0 2px rgba(0,194,255,0.08) !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--accent-cyan) !important;
    border: 2px solid var(--bg-base) !important;
    box-shadow: 0 0 10px rgba(0,194,255,0.6) !important;
    width: 16px !important; height: 16px !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[data-testid="stSliderTrackFill"] {
    background: linear-gradient(90deg, rgba(0,194,255,0.5), var(--accent-cyan)) !important;
}
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, rgba(0,194,255,0.08), rgba(0,194,255,0.04)) !important;
    border: 1px solid rgba(0,194,255,0.2) !important;
    border-radius: var(--radius-md) !important;
    color: var(--accent-cyan) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 12px 16px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: linear-gradient(135deg, rgba(0,194,255,0.15), rgba(0,194,255,0.08)) !important;
    border-color: rgba(0,194,255,0.4) !important;
    box-shadow: 0 0 16px rgba(0,194,255,0.2) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSidebar"] hr {
    border-color: var(--border-subtle) !important;
    margin: 1.5rem 0 !important;
}

/* ── TIPOGRAFIA ── */
h1, h2, h3 { font-family: var(--font-body) !important; }
h2 {
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    border: none !important;
    margin-bottom: 1rem !important;
}
hr { border-color: var(--border-subtle) !important; }

/* ── ANIMAZIONI ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes pulseGlow {
    0%, 100% { opacity: 0.7; box-shadow: 0 0 4px currentColor; }
    50%       { opacity: 1;   box-shadow: 0 0 12px currentColor; }
}

/* ── HEADER ── */
.ph-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2.2rem 0 1.8rem 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 2rem;
    animation: fadeSlideUp 0.6s ease both;
}
.ph-logo {
    font-family: var(--font-body);
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    background: linear-gradient(120deg, #FFFFFF 0%, #80DDFF 40%, var(--accent-cyan) 70%, #0077BB 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.ph-header-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.3rem;
}
.ph-subtitle {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--text-muted);
    letter-spacing: 0.14em;
    text-transform: uppercase;
}
.ph-tag {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 3px 10px;
    background: rgba(255,255,255,0.02);
}

/* ── SIGNAL BANNER ── */
.signal-banner {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    border-radius: var(--radius-md);
    padding: 1rem 1.6rem;
    margin-bottom: 2rem;
    border: 1px solid;
    animation: fadeSlideUp 0.6s 0.1s ease both;
}
.signal-banner.verde  { background: rgba(0,229,160,0.04);  border-color: rgba(0,229,160,0.18); }
.signal-banner.giallo { background: rgba(255,181,71,0.04);  border-color: rgba(255,181,71,0.18); }
.signal-banner.rosso  { background: rgba(255,90,90,0.04);   border-color: rgba(255,90,90,0.18); }
.signal-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.signal-dot.verde  { background: var(--accent-green); box-shadow: 0 0 0 4px rgba(0,229,160,0.12); animation: pulseGlow 2.5s infinite; color: var(--accent-green); }
.signal-dot.giallo { background: var(--accent-gold);  box-shadow: 0 0 0 4px rgba(255,181,71,0.12); }
.signal-dot.rosso  { background: var(--accent-red);   box-shadow: 0 0 0 4px rgba(255,90,90,0.12); }
.signal-label {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    white-space: nowrap;
}
.signal-banner.verde  .signal-label { color: var(--accent-green); }
.signal-banner.giallo .signal-label { color: var(--accent-gold); }
.signal-banner.rosso  .signal-label { color: var(--accent-red); }
.signal-text { font-family: var(--font-body); font-size: 0.88rem; color: var(--text-secondary); line-height: 1.4; }

/* ── KPI CARDS ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 1.6rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, transform 0.3s, box-shadow 0.3s;
    animation: fadeSlideUp 0.6s ease both;
    height: 100%;
    min-height: 180px;
    cursor: default;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-card:hover {
    border-color: rgba(0,194,255,0.2);
    transform: translateY(-3px);
    box-shadow: var(--shadow-md), var(--shadow-glow-c);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0,194,255,0.3) 50%, transparent 100%);
    opacity: 0;
    transition: opacity 0.3s;
}
.kpi-card:hover::before { opacity: 1; }
.kpi-card::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 140px; height: 140px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,194,255,0.04) 0%, transparent 70%);
    pointer-events: none;
}
.kpi-eyebrow {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-value {
    font-family: var(--font-body);
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.5rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-value.cyan  { color: var(--accent-cyan); }
.kpi-value.green { color: var(--accent-green); }
.kpi-value.gold  { color: var(--accent-gold); }
.kpi-value.red   { color: var(--accent-red); }
.kpi-sub {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-muted);
    line-height: 1.6;
    margin-bottom: 0.8rem;
}
.kpi-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-family: var(--font-mono);
    font-size: 0.58rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
}
.kpi-badge.green { background: var(--accent-green-dim); color: var(--accent-green); border: 1px solid rgba(0,229,160,0.2); }
.kpi-badge.gold  { background: var(--accent-gold-dim);  color: var(--accent-gold);  border: 1px solid rgba(255,181,71,0.2); }
.kpi-badge.red   { background: var(--accent-red-dim);   color: var(--accent-red);   border: 1px solid rgba(255,90,90,0.2); }

/* ── PANELS ── */
.panel {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 1.8rem 2rem;
    animation: fadeSlideUp 0.6s 0.2s ease both;
    height: 100%;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.panel:hover {
    border-color: var(--border-medium);
    box-shadow: var(--shadow-sm);
}
.panel-title {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 1.4rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.panel-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    transition: all 0.15s;
}
.panel-row:last-child { border-bottom: none; padding-bottom: 0; }
.panel-row:hover {
    background: rgba(255,255,255,0.025);
    margin: 0 -0.6rem;
    padding: 0.65rem 0.6rem;
    border-radius: 6px;
    border-bottom-color: transparent;
}
.panel-key {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--text-muted);
    letter-spacing: 0.02em;
}
.panel-val {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-align: right;
}
.panel-val.cyan  { color: var(--accent-cyan); }
.panel-val.green { color: var(--accent-green); }
.panel-val.red   { color: var(--accent-red); }
.panel-val.big   { font-size: 1.3rem; font-weight: 700; color: var(--accent-cyan); letter-spacing: -0.02em; }

/* ── CRISIS PANEL ── */
.crisis-panel {
    background: linear-gradient(135deg, rgba(255,90,90,0.04) 0%, rgba(10,17,24,0.95) 100%);
    border: 1px solid rgba(255,90,90,0.14);
    border-radius: var(--radius-xl);
    padding: 1.8rem 2rem;
    animation: fadeSlideUp 0.6s 0.2s ease both;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.crisis-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,90,90,0.3), transparent);
}
.crisis-header {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(255,90,90,0.5);
    margin-bottom: 1.4rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,90,90,0.1);
}
.crisis-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(255,90,90,0.06);
}
.crisis-row:last-child { border-bottom: none; }
.crisis-key { font-family: var(--font-mono); font-size: 0.68rem; color: rgba(255,90,90,0.4); }
.crisis-val { font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-secondary); font-weight: 500; }
.crisis-val.red   { color: var(--accent-red); }
.crisis-val.green { color: var(--accent-green); }
.crisis-impact {
    margin-top: 1.2rem;
    padding: 0.9rem 1.1rem;
    background: rgba(255,90,90,0.06);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(255,90,90,0.1);
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: rgba(255,90,90,0.5);
    text-align: center;
    letter-spacing: 0.05em;
}

/* ── SECTION LABEL ── */
.section-label {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 2.5rem 0 1.2rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--border-subtle); }

/* ── SIDEBAR SECTIONS ── */
.sb-section {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 1rem 0 0.5rem 0;
    margin-top: 0.5rem;
    border-top: 1px solid var(--border-subtle);
}
.sb-section:first-child { border-top: none; margin-top: 0; padding-top: 0; }

/* ── METRIC CARDS NATIVE ── */
.live-bar-wrap [data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
    animation: fadeSlideUp 0.6s 0.05s ease both;
}
.live-bar-wrap [data-testid="stMetric"]:hover {
    border-color: rgba(0,194,255,0.18);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm), 0 0 16px rgba(0,194,255,0.06);
}
.live-bar-wrap [data-testid="stMetricLabel"] {
    font-family: var(--font-mono) !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
.live-bar-wrap [data-testid="stMetricValue"] {
    font-family: var(--font-body) !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: var(--accent-cyan) !important;
    letter-spacing: -0.03em !important;
    line-height: 1.1 !important;
}
.live-bar-wrap [data-testid="stMetricDelta"] {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
}
.live-bar-wrap [data-testid="stMetricLabel"] svg {
    color: var(--text-muted) !important;
    transition: color 0.2s ease;
}
.live-bar-wrap [data-testid="stMetricLabel"]:hover svg {
    color: var(--accent-cyan) !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
    background: rgba(255,255,255,0.02) !important;
    color: var(--text-muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-medium) !important;
    padding: 12px 16px !important;
}
[data-testid="stDataFrame"] td {
    background: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    padding: 10px 16px !important;
}

/* ── FOOTER ── */
.ph-footer {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    border-top: 1px solid var(--border-subtle);
    margin-top: 3rem;
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    line-height: 2.2;
}

/* ── DELTA COLORI CUSTOM ── */
.ph-delta-green [data-testid="stMetricDelta"] { color: var(--accent-green) !important; }
.ph-delta-gold  [data-testid="stMetricDelta"] { color: var(--accent-gold)  !important; }
.ph-delta-red   [data-testid="stMetricDelta"] { color: var(--accent-red)   !important; }
.ph-delta-green [data-testid="stMetricDelta"] svg,
.ph-delta-gold  [data-testid="stMetricDelta"] svg,
.ph-delta-red   [data-testid="stMetricDelta"] svg { display: none !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.07); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.12); }
</style>""", unsafe_allow_html=True)


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

def calc_wcs(S, K, prem, n, crash, mult=100):
    Sc        = S * (1 - crash / 100)
    lc_gross  = max(K - Sc, 0)                  # perdita lorda per azione (senza premio)
    lc_net    = lc_gross - prem                  # perdita netta per azione (al netto del premio)
    return {
        "Sc":       round(Sc, 2),
        "lc":       round(lc_net, 2),            # per contratto, netto
        "lt_gross": round(lc_gross * n * mult, 2),  # perdita lorda totale
        "lt":       round(lc_net * n * mult, 2),    # perdita netta totale
        "pt":       round(prem * n * mult, 2),
        "crash":    crash,
    }

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
        key="iv_pct",
        help="Se hai premuto 'Aggiorna', questo campo viene preimpostato automaticamente con il VIX corrente.\nPuoi modificarlo manualmente per confrontare scenari diversi.")
    r_pct  = st.number_input("Tasso Risk-Free (%)", 0.0, 20.0, 4.5, 0.1,
        help="Rendimento BTP/Treasury 10 anni.\nAggiorna ogni 3 mesi circa.")

    st.markdown("<div class='sb-section'>Posizione & Rischio</div>", unsafe_allow_html=True)
    n_contratti = st.slider("Numero di Contratti", 1, 50, 3,
        help="Quanti contratti vuoi vendere.\nOgni contratto copre 100 azioni del sottostante.")
    marg_pct = st.slider("Margine Broker (%)", 5.0, 50.0, 15.0, 1.0,
        help="% del valore dello strike bloccata come garanzia dal broker.\nIBKR tipicamente richiede il 15-20% per le put OTM su ETF.\nVerifica nelle impostazioni del tuo conto.")
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

# Preimposta lo slider IV con il VIX aggiornato e ricarica la pagina
if aggiorna and vix_val is not None:
    st.session_state["iv_pct"] = float(vix_val)
    st.rerun()


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
# v5.1 — calcoli basati su n_contratti scelto dall'utente
mult      = 100                                        # ogni contratto = 100 azioni
mc        = round(K * mult * (marg_pct / 100), 2)     # margine per contratto (€)
marg_tot  = round(n_contratti * mc, 2)                 # margine totale richiesto (€)
ptot      = round(prem * n_contratti * mult, 2)        # incasso totale premi (€)
thday     = round(abs(gre["theta"]) * n_contratti * mult, 2)  # theta totale/giorno (€)
rend      = (ptot / marg_tot * 100) if marg_tot > 0 else 0    # rendimento sul margine (%)
dist      = (spot - K) / spot * 100
sc        = calc_wcs(spot, K, prem, n_contratti, crash)
# sz dict compatibilità (usato nel pannello e nel riepilogo)
sz        = {"n": n_contratti, "mc": mc, "imp": marg_tot, "lib": 0}

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
    <div style="display:flex;align-items:center;gap:1.2rem">
        <span class="ph-logo">Phinance</span>
        <div style="width:1px;height:2rem;background:var(--border-medium)"></div>
        <span class="ph-subtitle">Dashboard Vendita Put · Motore Black-Scholes</span>
    </div>
    <div class="ph-header-right">
        <span class="ph-tag">v5.1 · Yahoo Finance · CBOE VIX</span>
        <span style="font-family:var(--font-mono);font-size:0.55rem;color:var(--text-muted);letter-spacing:0.1em">SOLO A SCOPO EDUCATIVO</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── BARRA 4 DATI LIVE — frecce semantiche ──
# Usiamo delta_color="off" su tutti: Streamlit non aggiunge frecce proprie.
# Freccia e colore nel testo, poi CSS custom colora i delta per posizione.

# Prezzo Spot
if var > 0.05:
    spot_arrow = f"▲ +{var:.2f}% oggi"
    spot_cls   = "green"
elif var < -0.05:
    spot_arrow = f"▼ {var:.2f}% oggi"
    spot_cls   = "red"
else:
    spot_arrow = f"↔ {var:.2f}% oggi"
    spot_cls   = "gold"

# Vol. Storica: alta=verde, media=arancio, bassa=rosso
if vol_st >= 25:
    vol_arrow = "▲ Alta — Premi elevati"
    vol_cls   = "green"
elif vol_st >= 15:
    vol_arrow = "↔ Media — Nella norma"
    vol_cls   = "gold"
else:
    vol_arrow = "▼ Bassa — Premi scarsi"
    vol_cls   = "red"

# IV Rank: alto=verde, medio=arancio, basso=rosso
if iv_rank >= 60:
    ivr_arrow = "▲ Alto — Vendi"
    ivr_cls   = "green"
elif iv_rank >= 35:
    ivr_arrow = "↔ Medio — Valuta"
    ivr_cls   = "gold"
else:
    ivr_arrow = "▼ Basso — Aspetta"
    ivr_cls   = "red"

# VIX: alto=verde, medio=arancio, basso=rosso
if vix_val and vix_val >= 20:
    vix_arrow = "▲ Elevato — Buono per vendere"
    vix_cls   = "green"
elif vix_val and vix_val >= 15:
    vix_arrow = "↔ Normale — Nella norma"
    vix_cls   = "gold"
elif vix_val:
    vix_arrow = "▼ Basso — Premi scarsi"
    vix_cls   = "red"
else:
    vix_arrow = "Non disponibile"
    vix_cls   = "gold"


st.markdown("<div class='live-bar-wrap'>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns(4, gap="medium")

with b1:
    st.markdown(f"<div class='ph-delta-{spot_cls}'>", unsafe_allow_html=True)
    st.metric(
        label="● Prezzo Spot",
        value=f"{spot:,.2f}",
        delta=spot_arrow,
        delta_color="off",
        help=(
            "PREZZO SPOT\n\n"
            "Prezzo attuale del sottostante scaricato in tempo reale da Yahoo Finance.\n\n"
            f"Fonte: Yahoo Finance (chiusura)\n"
            f"Aggiornato: {ts_spot}"
        )
    )
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown(f"<div class='ph-delta-{vol_cls}'>", unsafe_allow_html=True)
    st.metric(
        label="● Vol. Storica 30gg",
        value=f"{vol_st:.1f}%",
        delta=vol_arrow,
        delta_color="off",
        help=(
            "VOLATILITÀ STORICA 30gg\n\n"
            "Quanto si è mosso davvero il mercato negli ultimi 30 giorni.\n"
            "Calcolata su rendimenti logaritmici giornalieri annualizzati (×√252).\n\n"
            "  ≥ 25% → Alta — premi elevati, favorevole per vendere\n"
            "  15-25% → Media — nella norma\n"
            "  < 15% → Bassa — premi scarsi, valuta se conviene\n\n"
            f"Fonte: Yahoo Finance (storico prezzi)\n"
            f"Aggiornato: {ts_vol}"
        )
    )
    st.markdown("</div>", unsafe_allow_html=True)

with b3:
    st.markdown(f"<div class='ph-delta-{ivr_cls}'>", unsafe_allow_html=True)
    st.metric(
        label="● IV Rank",
        value=f"{iv_rank:.0f} / 100",
        delta=ivr_arrow,
        delta_color="off",
        help=(
            "IV RANK (0 – 100)\n\n"
            "Dove si trova la volatilità attuale rispetto al suo range degli ultimi 12 mesi.\n\n"
            "  ≥ 60 → Alto — ottimo per vendere\n"
            "  35-59 → Medio — valuta con attenzione\n"
            "  < 35 → Basso — aspetta condizioni migliori\n\n"
            "Regola pratica: operare solo con IV Rank > 50\n\n"
            f"Fonte: Calcolato su dati Yahoo Finance\n"
            f"Aggiornato: {ts_ivr}"
        )
    )
    st.markdown("</div>", unsafe_allow_html=True)

with b4:
    st.markdown(f"<div class='ph-delta-{vix_cls}'>", unsafe_allow_html=True)
    st.metric(
        label="● VIX — Indice di Paura",
        value=vix_str,
        delta=vix_arrow,
        delta_color="off",
        help=(
            "VIX — CBOE VOLATILITY INDEX\n\n"
            "Misura la volatilità implicita attesa sull'S&P 500 nei prossimi 30 giorni.\n"
            "Viene scaricato in automatico e preimpostato nel campo IV della sidebar.\n\n"
            "  > 20 → Elevato — buono per vendere\n"
            "  15-20 → Normale — nella norma\n"
            "  < 15 → Basso — premi scarsi, evitare\n\n"
            f"Fonte: Yahoo Finance (^VIX)\n"
            f"Aggiornato: {ts_vix}"
        )
    )
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# variabili comuni
pn       = sc["lt"]                                        # perdita netta totale (già al netto del premio)
imp      = (abs(pn) / marg_tot * 100) if marg_tot > 0 else 0
rend_ann = (((1 + rend / 100) ** 12) - 1) * 100           # rendimento annuo composto

# ── SIGNAL BANNER ──
st.markdown(f"""
<div class="signal-banner {sema['c']}">
    <span class="signal-dot {sema['c']}"></span>
    <span class="signal-label">{sema['l']}</span>
    <span class="signal-text">{sema['d']}</span>
</div>
""", unsafe_allow_html=True)

# ── DETTAGLIO POSIZIONE — orizzontale full width, subito dopo semaforo ──
st.markdown(f"""
<div class="panel" style="margin-bottom:1.5rem">
    <div class="panel-title"><span style="color:var(--accent-green);margin-right:0.4rem">&#9678;</span> Dettaglio Posizione</div>
    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0">
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.4rem">Contratti selezionati</div>
            <div class="panel-val big cyan">{n_contratti}</div>
        </div>
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.4rem">Margine per contratto</div>
            <div class="panel-val cyan">{mc:,.0f} €</div>
        </div>
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.4rem">Margine totale richiesto</div>
            <div style="font-family:var(--font-mono);font-size:1rem;font-weight:700;color:var(--accent-gold)">{marg_tot:,.0f} €</div>
        </div>
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.4rem">Incasso totale premi</div>
            <div class="panel-val green">+{ptot:,.0f} €</div>
        </div>
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.4rem">Theta totale / giorno</div>
            <div class="panel-val green">+{thday:,.0f} €</div>
        </div>
        <div style="padding:0.6rem 1.2rem">
            <div class="panel-key" style="margin-bottom:0.4rem">Rendimento sul margine</div>
            <div class="panel-val green">{rend:.1f}% / mese · {rend_ann:.1f}% / anno (composto)</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS — 4 colonne ──
c1, c2, c3, c4 = st.columns(4, gap="medium")

with c1:
    st.markdown(f"""
    <div class="kpi-card" style="animation-delay:0.0s">
        <div class="kpi-eyebrow">🎯 Strike Consigliato</div>
        <div class="kpi-value cyan">{K:,.1f}</div>
        <div class="kpi-sub">{dist:.1f}% sotto lo spot</div>
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
        <div class="kpi-sub">Scade senza perdite</div>
        <div><span class="kpi-badge {bc}">{bt}</span></div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card" style="animation-delay:0.12s">
        <div class="kpi-eyebrow">◈ Premio Incassato</div>
        <div class="kpi-value green">{prem:.2f}</div>
        <div class="kpi-sub">{n_contratti} contratti → <strong style="color:var(--accent-green)">+{ptot:,.0f} €</strong></div>
        <div><span class="kpi-badge green">{rend:.1f}% sul margine / mese</span></div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card" style="animation-delay:0.18s">
        <div class="kpi-eyebrow">◎ Margine Richiesto</div>
        <div class="kpi-value gold">{marg_tot:,.0f} €</div>
        <div class="kpi-sub">{mc:,.0f} € × {n_contratti} contratti</div>
        <div><span class="kpi-badge gold">DA AVERE SUL CONTO</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# ── GRAFICO ──
st.plotly_chart(pnl_chart(spot, K, prem, sz["n"]), use_container_width=True)
st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

# ── GRECHE — orizzontale full width ──
st.markdown(f"""
<div class="panel" style="animation-delay:0.3s;margin-bottom:1.5rem">
    <div class="panel-title"><span style="color:var(--accent-cyan);margin-right:0.4rem">∑</span> Lettere Greche</div>
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0">
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.5rem">Δ Delta (prob. ITM)</div>
            <div class="panel-val cyan" style="font-size:1rem">{gre['delta']:.4f}</div>
            <div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--text-muted);margin-top:0.3rem">{abs(gre['delta'])*100:.1f}% prob. ITM</div>
        </div>
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.5rem">Γ Gamma</div>
            <div class="panel-val" style="font-size:1rem">{gre['gamma']:.6f}</div>
            <div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--text-muted);margin-top:0.3rem">accelerazione delta</div>
        </div>
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.5rem">Θ Theta</div>
            <div class="panel-val green" style="font-size:1rem">+{abs(gre['theta']):.4f} €</div>
            <div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--text-muted);margin-top:0.3rem">guadagno per giorno</div>
        </div>
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div class="panel-key" style="margin-bottom:0.5rem">ν Vega</div>
            <div class="panel-val" style="font-size:1rem">{gre['vega']:.4f}</div>
            <div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--text-muted);margin-top:0.3rem">sensib. a +1% IV</div>
        </div>
        <div style="padding:0.8rem 1.2rem">
            <div class="panel-key" style="margin-bottom:0.5rem">ρ Rho</div>
            <div class="panel-val" style="font-size:1rem">{gre['rho']:.4f}</div>
            <div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--text-muted);margin-top:0.3rem">sensib. ai tassi</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── SCENARIO CRISI — orizzontale full width ──
st.markdown(f"""
<div class="crisis-panel" style="animation-delay:0.35s">
    <div class="crisis-header">⚠ Scenario di Crisi — Crollo {sc['crash']:.0f}%</div>
    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0">
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08)">
            <div class="crisis-key" style="margin-bottom:0.4rem">Prezzo dopo il crollo</div>
            <div class="crisis-val">{sc['Sc']:,.2f}</div>
        </div>
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08)">
            <div class="crisis-key" style="margin-bottom:0.4rem">Perdita per contratto</div>
            <div class="crisis-val red">{sc['lc']:,.0f} €</div>
        </div>
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08)">
            <div class="crisis-key" style="margin-bottom:0.4rem">Perdita lorda totale</div>
            <div class="crisis-val red">{sc['lt_gross']:,.0f} €</div>
        </div>
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08)">
            <div class="crisis-key" style="margin-bottom:0.4rem">Premi già incassati</div>
            <div class="crisis-val green">+{sc['pt']:,.0f} €</div>
        </div>
        <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08)">
            <div class="crisis-key" style="margin-bottom:0.4rem">Perdita netta finale</div>
            <div class="crisis-val red" style="font-size:1rem;font-weight:700">{pn:,.0f} €</div>
        </div>
        <div style="padding:0.8rem 1.2rem">
            <div class="crisis-key" style="margin-bottom:0.4rem">Impatto sul margine</div>
            <div class="crisis-val red">{imp:.1f}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── RIEPILOGO ──
st.markdown("<div class='section-label'>Riepilogo Operazione</div>", unsafe_allow_html=True)
st.dataframe(pd.DataFrame({
    "Parametro": ["Strumento","Prezzo Attuale","Strike Consigliato","Distanza Strike",
                  "Giorni alla Scadenza","IV Impostata","Vol. Storica 30gg","VIX Corrente","IV Rank",
                  "Premio per Contratto","Numero Contratti","Margine per Contratto",
                  "Margine Totale Richiesto","Incasso Totale Premi",
                  "Punto di Pareggio","Theta Giornaliero","Rendimento sul Margine"],
    "Valore":    [nome, f"{spot:,.2f}", f"{K:,.2f}", f"{dist:.1f}% sotto lo spot",
                  f"{dte} gg", f"{iv_pct:.1f}%", f"{vol_st:.1f}%",
                  f"{vix_str}" + (" (preimpostato in IV)" if vix_val else ""),
                  f"{iv_rank:.0f}/100 — {ivr_label}",
                  f"{prem:.4f}  ({prem*100:.2f} € / contratto 100 azioni)",
                  str(n_contratti), f"{mc:,.0f} €",
                  f"{marg_tot:,.0f} € (da avere sul conto)",
                  f"+{ptot:,.0f} €",
                  f"{K-prem:,.2f}", f"+{thday:,.0f} € / giorno",
                  f"{rend:.1f}% / mese  ({rend_ann:.1f}% annuo composto stimato)"],
}), use_container_width=True, hide_index=True,
    column_config={
        "Parametro": st.column_config.TextColumn(width="medium"),
        "Valore":    st.column_config.TextColumn(width="large"),
    })

# ── FOOTER ──
st.markdown("""
<div class="ph-footer">
    <span style="font-size:0.72rem;color:var(--text-secondary);font-weight:500">Phinance</span><br>
    Sistemi Quantitativi per il Trading di Opzioni · v5.0<br>
    Dati: Yahoo Finance &nbsp;·&nbsp; VIX: CBOE &nbsp;·&nbsp; Motore: Black-Scholes<br>
    <span style="color:rgba(255,255,255,0.03);font-size:0.5rem">───────────────────────────────────────</span><br>
    Solo a scopo educativo · Non costituisce consulenza finanziaria
</div>
""", unsafe_allow_html=True)
