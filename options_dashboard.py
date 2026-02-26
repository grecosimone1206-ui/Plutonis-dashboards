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

# Logo Phinance (base64)
LOGO_B64 = "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"

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
    <div style="display:flex;align-items:center;gap:0.9rem">
        <img src="data:image/png;base64,{LOGO_B64}"
             style="height:44px;width:auto;filter:brightness(0) invert(1) sepia(1) saturate(5) hue-rotate(170deg);opacity:0.92;"
             alt="Phinance Logo">
        <div style="display:flex;align-items:baseline;gap:0.5rem">
            <span class="ph-logo">Phinance</span>
            <span class="ph-subtitle">Dashboard Vendita Put</span>
        </div>
    </div>
    <span class="ph-tag">Black-Scholes · Yahoo Finance · v4.0</span>
</div>
""", unsafe_allow_html=True)

# ── BARRA 4 DATI LIVE ──
fr  = "▲" if var >= 0 else "▼"
cls = "live-cell-change-up" if var >= 0 else "live-cell-change-down"

st.markdown(f"""
<div class="live-bar">

  <!-- PREZZO SPOT -->
  <div class="live-cell">
    <div class="live-cell-label">
      <span class="live-dot"></span>
      Prezzo Spot
      <span class="info-tooltip">?
        <span class="tooltip-content">
          <strong>Prezzo Spot</strong><br>
          Prezzo attuale del sottostante<br>
          scaricato da Yahoo Finance.<br>
          Fonte: Yahoo Finance (chiusura)<br>
          Aggiornato: {ts_spot}
        </span>
      </span>
    </div>
    <div class="live-cell-value cyan">{spot:,.2f}</div>
    <div class="{cls}">{fr} {abs(var):.2f}% oggi</div>
  </div>

  <!-- VOLATILITÀ STORICA -->
  <div class="live-cell">
    <div class="live-cell-label">
      <span class="live-dot"></span>
      Vol. Storica 30gg
      <span class="info-tooltip">?
        <span class="tooltip-content">
          <strong>Volatilità Storica 30gg</strong><br>
          Quanto si è mosso davvero il<br>
          mercato negli ultimi 30 giorni.<br>
          Calcolata su rendimenti log giornalieri<br>
          annualizzati (×√252).<br>
          Fonte: Yahoo Finance (storico prezzi)<br>
          Aggiornato: {ts_vol}
        </span>
      </span>
    </div>
    <div class="live-cell-value">{vol_st:.1f}%</div>
    <div class="live-cell-sub">Volatilità realizzata annualizzata</div>
  </div>

  <!-- IV RANK -->
  <div class="live-cell">
    <div class="live-cell-label">
      <span class="live-dot"></span>
      IV Rank
      <span class="info-tooltip">?
        <span class="tooltip-content">
          <strong>IV Rank (0–100)</strong><br>
          Dove si trova la vol. attuale rispetto<br>
          al suo range degli ultimi 12 mesi.<br>
          100 = al massimo storico dell'anno<br>
          0   = al minimo storico dell'anno<br>
          Sopra 50 = buono per vendere<br>
          Fonte: Calcolato su dati Yahoo Finance<br>
          Aggiornato: {ts_ivr}
        </span>
      </span>
    </div>
    <div class="live-cell-value {'green' if iv_rank >= 60 else 'gold' if iv_rank >= 35 else 'red'}">{iv_rank:.0f}<span style="font-size:1rem;color:var(--text-muted)">/100</span></div>
    <div><span class="ivr-badge {ivr_cls}">{ivr_label}</span></div>
  </div>

  <!-- VIX -->
  <div class="live-cell">
    <div class="live-cell-label">
      <span class="live-dot"></span>
      VIX — Indice di Paura
      <span class="info-tooltip">?
        <span class="tooltip-content">
          <strong>VIX (CBOE Volatility Index)</strong><br>
          Volatilità implicita dell'S&P 500.<br>
          Preimpostato automaticamente nel<br>
          campo IV quando premi Aggiorna.<br>
          VIX &lt;15 = basso (rosso)<br>
          VIX 15-20 = normale (giallo)<br>
          VIX &gt;20 = alto (verde)<br>
          Fonte: Yahoo Finance (^VIX)<br>
          Aggiornato: {ts_vix}
        </span>
      </span>
    </div>
    <div class="live-cell-value {vix_cls}">{vix_str}</div>
    <div class="live-cell-sub">{'Preimpostato in IV ✓' if vix_val else 'Non disponibile'}</div>
  </div>

</div>
""", unsafe_allow_html=True)

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
