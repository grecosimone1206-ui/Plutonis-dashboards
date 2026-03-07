"""
╔══════════════════════════════════════════════════════════╗
║         PHINANCE - Dashboard Vendita Put  v5.1           ║
║         Auto VIX &middot; IV Rank &middot; Live Timestamps             ║
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

# &mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;──────────────────
# CONFIGURAZIONE PAGINA
# &mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;──────────────────
st.set_page_config(
    page_title="Phinance | Dashboard Opzioni",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
# STRATEGIA — SPLASH SCREEN
# ═══════════════════════════════════════════════════════════

if "strategia" not in st.session_state:
    st.session_state.strategia = None

if st.session_state.strategia is None:

    # ── CSS globale splash ──
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700;9..40,800&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"] {
    background: #07090D !important;
    margin: 0; padding: 0;
}
[data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stSidebar"]   { display: none !important; }
[data-testid="stToolbar"]   { display: none !important; }
[data-testid="stDecoration"]{ display: none !important; }
footer                       { display: none !important; }
#MainMenu                    { display: none !important; }

/* ── Pulsanti Streamlit = Tab visibili ── */

/* Contenitore colonne centrato */
div[data-testid="stHorizontalBlock"] {
    justify-content: center !important;
    gap: 1rem !important;
    max-width: 460px !important;
    margin: 0 auto !important;
}

/* Reset colonne */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    padding: 0 !important;
}

/* Il pulsante stesso — stile tab rosso */
div[data-testid="stHorizontalBlock"] .stButton > button {
    position: relative !important;
    min-width: 210px !important;
    height: 54px !important;
    padding: 0 2.2rem !important;
    border-radius: 14px !important;
    border: 1px solid rgba(180,28,28,0.32) !important;
    background: rgba(160,22,22,0.07) !important;
    color: rgba(255,255,255,0.68) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    cursor: pointer !important;
    overflow: hidden !important;
    transition:
        border-color 0.25s ease,
        color        0.25s ease,
        box-shadow   0.25s ease,
        transform    0.2s  ease,
        background   0.25s ease !important;
    bottom: unset !important;
    left: unset !important;
    opacity: 1 !important;
    pointer-events: all !important;
    width: auto !important;
    box-shadow: none !important;
    outline: none !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: rgba(220,45,45,0.68) !important;
    color: #ffffff !important;
    background: rgba(200,30,30,0.12) !important;
    box-shadow:
        0 0 22px  5px rgba(200,28,28,0.20),
        0 0 50px 12px rgba(200,28,28,0.09),
        inset 0 0 18px rgba(200,28,28,0.07) !important;
    transform: translateY(-2px) !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button:active {
    transform: translateY(0) !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button:focus {
    outline: none !important;
    box-shadow:
        0 0 22px  5px rgba(200,28,28,0.20),
        0 0 50px 12px rgba(200,28,28,0.09) !important;
}


/* ── KEYFRAMES ── */
@keyframes spin-ring {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes breathe {
    0%,100% { opacity: 0.55; }
    50%      { opacity: 1;    }
}
@keyframes fade-up {
    from { opacity:0; transform:translateY(22px); }
    to   { opacity:1; transform:translateY(0);    }
}
@keyframes dot-beat {
    0%,100% { box-shadow: 0 0 8px 2px rgba(210,35,35,0.7), 0 0 20px 4px rgba(210,35,35,0.3); }
    50%      { box-shadow: 0 0 14px 4px rgba(255,60,60,1),  0 0 36px 8px rgba(255,60,60,0.5); }
}

/* ── SPLASH ROOT ── */
.ph-splash {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding-top: calc(50vh - 260px);
    background: #07090D;
    animation: fade-up 0.8s cubic-bezier(.22,.68,0,1.2) both;
}

/* radial ambient */
.ph-splash::before {
    content:'';
    position:absolute;
    top:38%; left:50%;
    transform:translate(-50%,-50%);
    width:700px; height:700px;
    background: radial-gradient(circle, rgba(180,25,25,0.055) 0%, transparent 65%);
    pointer-events:none;
}

/* ── RING WRAPPER ── */
.ph-ring-wrap {
    position: relative;
    width: 320px;
    height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 3.2rem;
}

/* Rotating conic arc */
.ph-ring-spin {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: conic-gradient(
        from 0deg,
        transparent 0%,
        transparent 55%,
        rgba(200,30,30,0.00) 65%,
        rgba(215,45,45,0.45) 76%,
        rgba(240,70,70,0.80) 84%,
        rgba(255,110,110,1)  90%,
        rgba(240,70,70,0.80) 96%,
        rgba(210,35,35,0.30) 100%
    );
    -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 1.8px), #fff calc(100% - 0.5px));
    mask:         radial-gradient(farthest-side, transparent calc(100% - 1.8px), #fff calc(100% - 0.5px));
    animation: spin-ring 3.8s linear infinite;
    filter: blur(0.3px);
}

/* Soft outer glow ring (static, breathing) */
.ph-ring-glow {
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    border: 1px solid rgba(200,30,30,0.12);
    box-shadow:
        0 0 24px 6px  rgba(180,20,20,0.10),
        0 0 60px 14px rgba(180,20,20,0.05);
    animation: breathe 4.5s ease-in-out infinite;
}

/* Inner decorative rings */
.ph-ring-d1 {
    position:absolute; inset:14px;
    border-radius:50%;
    border:1px solid rgba(255,255,255,0.035);
}
.ph-ring-d2 {
    position:absolute; inset:28px;
    border-radius:50%;
    border:1px solid rgba(255,255,255,0.020);
}

/* ── LOGO TEXT ── */
.ph-logo-text {
    position: relative;
    z-index: 10;
    font-family: 'DM Sans', sans-serif;
    font-size: 4rem;
    font-weight: 800;
    letter-spacing: -0.045em;
    line-height: 1;
    /* white → pale blue gradient, replicates the image reference */
    background: linear-gradient(
        160deg,
        #FFFFFF  0%,
        #D8E8FF 35%,
        #7BBCFF 65%,
        #4AA0FF 100%
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 2px 24px rgba(100,180,255,0.18));
    user-select: none;
}

/* Accent dot after text */
.ph-logo-text::after {
    content: '';
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #CC2020;
    margin-left: 5px;
    margin-bottom: 7px;
    vertical-align: bottom;
    box-shadow: 0 0 8px 2px rgba(210,35,35,0.7), 0 0 20px 4px rgba(210,35,35,0.3);
    animation: dot-beat 3.8s ease-in-out infinite;
    -webkit-text-fill-color: initial;
}

/* ── TABS ── */
.ph-tabs {
    display: flex;
    gap: 1rem;
    animation: fade-up 0.9s 0.15s cubic-bezier(.22,.68,0,1.2) both;
}

.ph-tab {
    position: relative;
    min-width: 210px;
    padding: 1rem 2.2rem;
    border-radius: 14px;
    border: 1px solid rgba(180,28,28,0.30);
    background: rgba(160,22,22,0.07);
    color: rgba(255,255,255,0.68);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    text-align: center;
    cursor: pointer;
    user-select: none;
    overflow: hidden;
    transition:
        border-color   0.25s ease,
        color          0.25s ease,
        box-shadow     0.25s ease,
        transform      0.2s  ease,
        background     0.25s ease;
}

/* top shimmer line */
.ph-tab::after {
    content:'';
    position:absolute;
    top:0; left:15%; right:15%;
    height:1px;
    background: linear-gradient(90deg, transparent, rgba(255,80,80,0.55), transparent);
    opacity:0;
    transition: opacity 0.25s ease;
    border-radius:1px;
}

.ph-tab:hover {
    border-color: rgba(220,45,45,0.65);
    color: #ffffff;
    background: rgba(200,30,30,0.11);
    box-shadow:
        0  0 22px  5px rgba(200,28,28,0.18),
        0  0 50px 12px rgba(200,28,28,0.08),
        inset 0 0 18px rgba(200,28,28,0.06);
    transform: translateY(-2px);
}
.ph-tab:hover::after { opacity:1; }
.ph-tab:active { transform: translateY(0); }

</style>
""", unsafe_allow_html=True)

    # ── HTML della splash (logo + ring, senza tab HTML) ──
    st.markdown("""
<div class="ph-splash">

  <div class="ph-ring-wrap">
    <div class="ph-ring-glow"></div>
    <div class="ph-ring-spin"></div>
    <div class="ph-ring-d1"></div>
    <div class="ph-ring-d2"></div>
    <span class="ph-logo-text">Phinance</span>
  </div>

</div>
""", unsafe_allow_html=True)

    # ── Pulsanti Streamlit invisibili sovrapposti ai tab via CSS ──
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Put Scoperta", key="splash_ps"):
            st.session_state.strategia = "put_scoperta"
            st.rerun()
    with col2:
        if st.button("Bull Put Spread", key="splash_bps"):
            st.session_state.strategia = "bull_put_spread"
            st.rerun()

    st.stop()

STRATEGIA = st.session_state.strategia


st.markdown("""
<style>
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
  font-variant-numeric: normal;
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
* { font-variant-numeric: normal !important; }

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
    overflow: visible;
    transition: border-color 0.3s, transform 0.3s, box-shadow 0.3s;
    animation: fadeSlideUp 0.6s ease both;
    height: 100%;
    min-height: 155px;
    cursor: default;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-card.mini {
    min-height: unset !important;
    height: 115px !important;
    padding: 0.9rem 1rem !important;
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
    overflow: visible;
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
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-secondary);
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
    color: var(--text-secondary);
    letter-spacing: 0.02em;
    font-weight: 500;
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
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(255,150,150,0.95);
    margin-bottom: 1.4rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,90,90,0.2);
}
.crisis-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(255,90,90,0.06);
}
.crisis-row:last-child { border-bottom: none; }
.crisis-key { font-family: var(--font-mono); font-size: 0.63rem; color: rgba(255,150,150,0.9); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
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
    font-family: var(--font-body);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    text-transform: none;
    color: var(--accent-cyan);
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
/* :has() necessario perché il div wrapper e st.metric sono fratelli nel DOM, non padre-figlio */
[data-testid="stColumn"]:has(.ph-delta-green) [data-testid="stMetricDelta"] { color: var(--accent-green) !important; }
[data-testid="stColumn"]:has(.ph-delta-gold)  [data-testid="stMetricDelta"] { color: var(--accent-gold)  !important; }
[data-testid="stColumn"]:has(.ph-delta-red)   [data-testid="stMetricDelta"] { color: var(--accent-red)   !important; }
[data-testid="stColumn"]:has(.ph-delta-green) [data-testid="stMetricDelta"] svg,
[data-testid="stColumn"]:has(.ph-delta-gold)  [data-testid="stMetricDelta"] svg,
[data-testid="stColumn"]:has(.ph-delta-red)   [data-testid="stMetricDelta"] svg { display: none !important; }
/* ── SPLASH SCREEN ── */
.splash-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
    padding: 2rem;
    animation: fadeSlideUp 0.8s ease both;
}
.splash-logo {
    font-family: var(--font-body);
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #00C2FF 0%, #00E5A0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
}
.splash-sub {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 3rem;
}
.splash-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    width: 100%;
    max-width: 760px;
}
.splash-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 2rem 2rem 1.8rem;
    cursor: pointer;
    transition: border-color 0.3s, transform 0.3s, box-shadow 0.3s;
    position: relative;
    overflow: hidden;
}
.splash-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--card-accent, #00C2FF), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
.splash-card:hover {
    border-color: var(--border-strong);
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}
.splash-card:hover::before { opacity: 1; }
.splash-card-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
}
.splash-card-title {
    font-family: var(--font-body);
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.4rem;
    letter-spacing: -0.02em;
}
.splash-card-sub {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.splash-card-desc {
    font-family: var(--font-body);
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1.2rem;
}
.splash-card-badge {
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 0.55rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.7rem;
    border-radius: 100px;
    border: 1px solid;
}
.splash-card-badge.cyan {
    color: var(--accent-cyan);
    border-color: rgba(0,194,255,0.25);
    background: rgba(0,194,255,0.06);
}
.splash-card-badge.green {
    color: var(--accent-green);
    border-color: rgba(0,229,160,0.25);
    background: rgba(0,229,160,0.06);
}
.splash-footer {
    font-family: var(--font-mono);
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    margin-top: 2.5rem;
    text-align: center;
}
/* Pannello analisi spread BPS */
.spread-analysis {
    background: linear-gradient(135deg, rgba(0,229,160,0.04) 0%, rgba(0,194,255,0.04) 100%);
    border: 1px solid rgba(0,229,160,0.15);
    border-radius: var(--radius-xl);
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.5rem;
    animation: fadeSlideUp 0.6s ease both;
    animation-delay: 0.25s;
}
.spread-analysis-title {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent-green);
    margin-bottom: 1rem;
}
.spread-rule {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    padding: 0.5rem 0.9rem;
    border-radius: 8px;
    display: inline-block;
    margin-top: 0.4rem;
}
.spread-rule.ok {
    background: rgba(0,229,160,0.08);
    border: 1px solid rgba(0,229,160,0.2);
    color: var(--accent-green);
}
.spread-rule.warn {
    background: rgba(255,181,71,0.08);
    border: 1px solid rgba(255,181,71,0.2);
    color: var(--accent-gold);
}
.spread-rule.bad {
    background: rgba(255,90,90,0.08);
    border: 1px solid rgba(255,90,90,0.2);
    color: var(--accent-red);
}

/* ── TOOLTIP GRECHE ── */
.greek-tooltip {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}
.greek-tooltip .tip-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 13px; height: 13px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    font-size: 0.5rem;
    color: var(--text-muted);
    cursor: help;
    font-family: var(--font-body);
    font-style: normal;
    flex-shrink: 0;
    transition: background 0.2s, border-color 0.2s;
}
.greek-tooltip:hover .tip-icon {
    background: rgba(0,194,255,0.12);
    border-color: rgba(0,194,255,0.3);
    color: var(--accent-cyan);
}
.greek-tooltip .tip-box {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 0;
    min-width: 220px;
    max-width: 260px;
    background: #0F1E2E;
    border: 1px solid rgba(0,194,255,0.2);
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    font-family: var(--font-body);
    font-size: 0.72rem;
    color: var(--text-secondary);
    line-height: 1.5;
    z-index: 9999;
    box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    transition: opacity 0.2s, visibility 0.2s;
    pointer-events: none;
    white-space: normal;
    text-transform: none;
    letter-spacing: 0;
}
.greek-tooltip:hover .tip-box {
    visibility: visible;
    opacity: 1;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.07); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.12); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FUNZIONI DATI &mdash; yfinance + VIX + IV Rank
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
    try:
        import pytz
        tz = pytz.timezone("Europe/Rome")
        return datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
    except ImportError:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def fmt(value, decimals=2) -> str:
    """Formato europeo: separatore migliaia = punto, decimale = virgola."""
    s = f"{value:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

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

def calc_semaforo(iv, vol, ivr, vix=None):
    """Usa sia IV vs Vol.Storica che IV Rank per segnale più preciso."""
    ratio = iv/vol if vol > 0 else 1.0
    # Verde se entrambi i segnali sono positivi
    if ratio >= 1.20 and ivr >= 50:
        return {"c":"verde",  "l":"Condizioni Ottime",      "d":f"VIX {fmt(vix,2) if vix else fmt(iv,1)+'%'} &middot; IV Rank {fmt(ivr,0)}/100 &mdash; premi gonfiati, ottimo per vendere"}
    if ratio >= 1.20 or ivr >= 50:
        return {"c":"giallo", "l":"Condizioni Parzialmente Favorevoli", "d":f"VIX {fmt(vix,2) if vix else fmt(iv,1)+'%'} &middot; IV Rank {fmt(ivr,0)}/100 &mdash; un segnale positivo, l'altro neutro. Valutare con attenzione"}
    if ratio >= 0.85:
        return {"c":"giallo", "l":"Condizioni nella Norma",  "d":f"VIX {fmt(vix,2) if vix else fmt(iv,1)+'%'} &middot; IV Rank {fmt(ivr,0)}/100 &mdash; valutare il premio"}
    return          {"c":"rosso",  "l":"Condizioni Sfavorevoli",  "d":f"VIX {fmt(vix,2) if vix else fmt(iv,1)+'%'} &middot; IV Rank {fmt(ivr,0)}/100 &mdash; premi insufficienti, meglio aspettare"}

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
        hovertemplate='<b>Prezzo:</b> %{x:,.2f}<br><b>P&L:</b> %{y:+,.0f} &euro;<extra></extra>'))
    fig.add_vline(x=K,       line=dict(color='#FFB547', dash='dash', width=1), annotation=dict(text=f"Strike {fmt(K,0)}",   font=dict(color='#FFB547', size=11)))
    fig.add_vline(x=S,       line=dict(color='rgba(255,255,255,0.2)', dash='dot', width=1), annotation=dict(text=f"Spot {fmt(S,0)}", font=dict(color='#8B9FC0', size=11)))
    fig.add_vline(x=K-prem,  line=dict(color='#A855F7', dash='dash', width=1), annotation=dict(text=f"Pareggio {fmt(K-prem,0)}", font=dict(color='#A855F7', size=11)))
    fig.add_hline(y=0,       line=dict(color='rgba(255,255,255,0.08)', width=1))
    fig.update_layout(
        paper_bgcolor='#080C10', plot_bgcolor='#0C1219',
        font=dict(family='DM Mono', size=11, color='#8B9FC0'),
        title=dict(text='Profilo Profitto / Perdita a Scadenza', font=dict(family='DM Sans', size=13, color='#8B9FC0'), x=0, xanchor='left', pad=dict(l=0,b=12)),
        xaxis=dict(title='Prezzo del Sottostante a Scadenza', gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)', tickfont=dict(size=10), title_font=dict(size=11)),
        yaxis=dict(title='Profitto / Perdita (&euro;)',            gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)', tickfont=dict(size=10), title_font=dict(size=11)),
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
    # Pulsante cambia strategia
    strat_label = "&#9679; Put Scoperta" if STRATEGIA == "put_scoperta" else "&#9670; Bull Put Spread"
    st.markdown(f"<div style='font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted);letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.4rem'>Strategia attiva</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-family:var(--font-body);font-size:0.9rem;font-weight:600;color:var(--accent-cyan);margin-bottom:0.6rem'>{strat_label}</div>", unsafe_allow_html=True)
    if st.button("&#8635; Cambia strategia", use_container_width=True):
        st.session_state.strategia = None
        st.rerun()
    st.markdown("<hr style='border:none;border-top:1px solid var(--border-subtle);margin:1rem 0'>", unsafe_allow_html=True)

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

    aggiorna = st.button("&#8635;  Aggiorna Tutti i Dati")

    st.markdown("<div class='sb-section'>Parametri Opzione</div>", unsafe_allow_html=True)

    dte    = st.slider("Giorni alla Scadenza (DTE)", 1, 365, 45,
        help=f"Giorni calendariali alla scadenza.\nOttimale: 35-49 giorni.\nUltimo aggiornamento: impostato da te manualmente.")
    iv_pct = st.slider("Volatilità Implicita IV (%)", 1.0, 150.0,
        float(st.session_state.get("_iv_pct_init", 20.0)), 0.5,
        key="iv_pct_slider",
        help="Se hai premuto 'Aggiorna', questo campo viene preimpostato automaticamente con il VIX corrente.\nPuoi modificarlo manualmente per confrontare scenari diversi.")
    r_pct  = st.number_input("Tasso Risk-Free (%)", 0.0, 20.0, 4.5, 0.1,
        help="Rendimento BTP/Treasury 10 anni.\nAggiorna ogni 3 mesi circa.")

    st.markdown("<div class='sb-section'>Posizione & Rischio</div>", unsafe_allow_html=True)
    n_contratti = st.slider("Numero di Contratti", 1, 50, 3,
        help="Quanti contratti vuoi vendere.\nOgni contratto copre 100 azioni del sottostante.")
    marg_pct = st.slider("Margine Broker (%)", 5.0, 50.0, 15.0, 1.0,
        help="% del valore dello strike bloccata come garanzia dal broker.\nIl broker tipicamente richiede il 15-20% per le put OTM su ETF.\nVerifica nelle impostazioni del tuo conto.")
    crash    = st.slider("Scenario di Crisi (%)", 5.0, 50.0, 20.0, 1.0,
        help="Crollo ipotetico usato per calcolare il worst case scenario.")

    st.markdown("<div class='sb-section'>Obiettivo Strategia</div>", unsafe_allow_html=True)
    prob_t = st.slider("Probabilità di Successo (%)", 70.0, 99.0, 84.0, 1.0,
        help="84% = Delta 0.16 — punto ottimale per la strategia.\n90% = Delta 0.10 — più conservativo.\n80% = Delta 0.20 — più aggressivo.")

    # Parametri specifici Bull Put Spread
    if STRATEGIA == "bull_put_spread":
        st.markdown("<div class='sb-section'>Parametri Spread</div>", unsafe_allow_html=True)
        larghezza_spread = st.select_slider("Larghezza Spread ($)",
            options=[5, 10, 15, 20, 25, 30, 50], value=10,
            help="Differenza in dollari tra lo strike venduto e quello comprato.\nSpread da $10 è lo standard per SPY/QQQ.")
        credito_reale_bps = st.number_input("Credito netto incassato ($)",
            min_value=0.01, max_value=500.0,
            value=float(st.session_state.get("_credito_bps", 1.38)), step=0.01,
            format="%.2f",
            help="Il credito netto = premio put venduta - premio put comprata.\nLeggilo direttamente dal tuo broker.")
        st.session_state["_credito_bps"] = credito_reale_bps
        # Calcolo % credito su larghezza
        pct_credito = (credito_reale_bps / larghezza_spread) * 100
        if pct_credito >= 30:
            cred_color = "var(--accent-green)"; cred_label = "Ottimale"
        elif pct_credito >= 25:
            cred_color = "var(--accent-gold)"; cred_label = "Accettabile"
        else:
            cred_color = "var(--accent-red)"; cred_label = "Insufficiente"
        st.markdown(
            f"<div style='font-family:var(--font-mono);font-size:0.72rem;color:{cred_color};"
            f"background:rgba(0,0,0,0.2);border:1px solid {cred_color}33;"
            f"border-radius:6px;padding:6px 10px;margin-top:0.3rem'>"
            f"{pct_credito:.1f}% della larghezza &mdash; <strong>{cred_label}</strong></div>",
            unsafe_allow_html=True
        )
    else:
        larghezza_spread = None
        credito_reale_bps = None

    st.markdown("<div class='sb-section'>Dati Reali dal Broker</div>", unsafe_allow_html=True)

    # ── IV Rank manuale ──
    usa_ivrank_reale = st.toggle("Usa IV Rank reale",
        help="Attiva per inserire l'IV Rank reale che vedi nella schermata del tuo broker.")
    if usa_ivrank_reale:
        st.markdown("<span style='font-family:var(--font-mono);font-size:0.6rem;color:var(--text-muted);letter-spacing:0.1em'>IV RANK REALE (0&ndash;100)</span>", unsafe_allow_html=True)
        iv_rank_reale = st.number_input("IV Rank reale", 0.0, 100.0,
            float(st.session_state.get("_ivr_val", 50.0)), 0.1,
            label_visibility="collapsed", key="input_ivr", format="%.1f")
        st.session_state["_ivr_val"] = iv_rank_reale
        st.markdown(
            f"<div style='font-family:var(--font-mono);font-size:0.72rem;color:var(--accent-cyan);"
            f"background:rgba(0,194,255,0.06);border:1px solid rgba(0,194,255,0.15);"
            f"border-radius:6px;padding:6px 10px;margin-top:0.3rem'>"
            f"IV Rank selezionato: <strong>{iv_rank_reale:.1f} / 100</strong></div>",
            unsafe_allow_html=True
        )
    else:
        iv_rank_reale = None

    # ── Greche reali — solo put scoperta ──
    if STRATEGIA == "put_scoperta":
        usa_greche_reali = st.toggle("Usa greche reali",
            help="Attiva per inserire Delta e Theta reali che vedi sul tuo broker.")
        if usa_greche_reali:
            st.markdown("<span style='font-family:var(--font-mono);font-size:0.6rem;color:var(--text-muted);letter-spacing:0.1em'>DELTA REALE</span>", unsafe_allow_html=True)
            delta_reale = st.number_input("Delta reale", 0.0, 1.0,
                float(st.session_state.get("_delta_val", 0.20)), 0.01,
                label_visibility="collapsed", key="input_delta", format="%.2f")
            st.session_state["_delta_val"] = delta_reale
            st.markdown("<span style='font-family:var(--font-mono);font-size:0.6rem;color:var(--text-muted);letter-spacing:0.1em'>THETA REALE (&euro;/giorno)</span>", unsafe_allow_html=True)
            theta_reale = st.number_input("Theta reale", 0.0, 9999.0,
                float(st.session_state.get("_theta_val", 10.0)), 0.01,
                label_visibility="collapsed", key="input_theta", format="%.2f")
            st.session_state["_theta_val"] = theta_reale
            st.markdown(
                f"<div style='font-family:var(--font-mono);font-size:0.72rem;color:var(--accent-cyan);"
                f"background:rgba(0,194,255,0.06);border:1px solid rgba(0,194,255,0.15);"
                f"border-radius:6px;padding:6px 10px;margin-top:0.3rem'>"
                f"&#916; {delta_reale:.2f} &nbsp;&middot;&nbsp; &#920; +{theta_reale:.2f} &euro;/gg</div>",
                unsafe_allow_html=True
            )
        else:
            delta_reale = None
            theta_reale = None
    else:
        delta_reale = None
        theta_reale = None

    # ── Premio reale — solo put scoperta ──
    if STRATEGIA == "put_scoperta":
        usa_premio_reale = st.toggle("Usa premio reale",
            help="Attiva per inserire il premio reale che vedi sul tuo broker invece di quello calcolato da Black-Scholes.")
        if usa_premio_reale:
            st.markdown("<span style='font-family:var(--font-mono);font-size:0.6rem;color:var(--text-muted);letter-spacing:0.1em'>PREMIO REALE (BID) &mdash; &euro;</span>", unsafe_allow_html=True)

            def _sync_slider():
                st.session_state["_pr_val"] = st.session_state["slider_pr"]
            def _sync_input():
                st.session_state["_pr_val"] = st.session_state["input_pr"]

            if "_pr_val" not in st.session_state:
                st.session_state["_pr_val"] = 5.0

            cur = float(st.session_state["_pr_val"])
            col_s, col_n = st.columns([2, 1])
            with col_s:
                st.slider(
                    "Premio (cursore)", 0.01, 500.0, cur, 0.01,
                    label_visibility="collapsed",
                    key="slider_pr",
                    on_change=_sync_slider
                )
            with col_n:
                st.number_input(
                    "Premio (±)", 0.01, 500.0, cur, 0.01,
                    label_visibility="collapsed",
                    key="input_pr",
                    format="%.2f",
                    on_change=_sync_input
                )
            premio_reale = float(st.session_state["_pr_val"])
            st.markdown(
                f"<div style='font-family:var(--font-mono);font-size:0.72rem;color:var(--accent-cyan);"
                f"background:rgba(0,194,255,0.06);border:1px solid rgba(0,194,255,0.15);"
                f"border-radius:6px;padding:6px 10px;margin-top:0.3rem'>"
                f"Premio selezionato: <strong>{premio_reale:.2f} &euro;</strong></div>",
                unsafe_allow_html=True
            )
        else:
            premio_reale = None
    else:
        premio_reale = None


# ═══════════════════════════════════════════════════════════
# RECUPERO DATI
# ═══════════════════════════════════════════════════════════

if ("dati" not in st.session_state or aggiorna or
        st.session_state.get("tk") != tk):
    with st.spinner(f"&#10227;  Recupero dati per {tk} e VIX…"):
        st.session_state.dati = recupera_dati_mercato(tk)
        st.session_state.tk   = tk

dati = st.session_state.dati
if dati.get("errore"):
    st.error(f"**Errore dati:** {dati['errore']}")
    st.info("💡 Prova con: SPY &middot; QQQ &middot; AAPL &middot; TSLA &middot; MSFT &middot; ^GSPC")
    st.stop()

spot    = dati["prezzo_spot"]
vol_st  = dati["vol_storica"]
iv_rank = iv_rank_reale if iv_rank_reale is not None else dati["iv_rank"]
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
    st.session_state["_iv_pct_init"] = float(vix_val)
    st.rerun()


# ═══════════════════════════════════════════════════════════
# CALCOLI
# ═══════════════════════════════════════════════════════════

T     = dte / 365.0
sigma = iv_pct / 100.0
r     = r_pct / 100.0
K     = strike_target(spot, sigma, T, r, prob_t/100.0)
par   = Par(S=spot, K=K, T=T, r=r, sigma=sigma)
prem_bs = prezzo_put(par)
prem     = premio_reale if premio_reale is not None else prem_bs
prem_fonte = "Reale (broker)" if premio_reale is not None else "Black-Scholes (stimato)"
prob  = prob_ok(par)
gre   = calc_greche(par)
sema  = calc_semaforo(iv_pct, vol_st, iv_rank, vix_val)
# v5.1 &mdash; calcoli basati su n_contratti scelto dall'utente
mult      = 100                                        # ogni contratto = 100 azioni
mc        = round(K * mult * (marg_pct / 100), 2)     # margine per contratto (&euro;)
marg_tot  = round(n_contratti * mc, 2)                 # margine totale richiesto (&euro;)
ptot      = round(prem * n_contratti * mult, 2)        # incasso totale premi (&euro;)
thday     = round(abs(gre["theta"]) * n_contratti * mult, 2)  # theta totale/giorno (&euro;)
rend      = (ptot / marg_tot * 100) if marg_tot > 0 else 0    # rendimento sul margine (%)
dist      = (spot - K) / spot * 100
sc        = calc_wcs(spot, K, prem, n_contratti, crash)
# sz dict compatibilità (usato nel pannello e nel riepilogo)
sz        = {"n": n_contratti, "mc": mc, "imp": marg_tot, "lib": 0}

# ── CALCOLI BULL PUT SPREAD ──
if STRATEGIA == "bull_put_spread" and larghezza_spread and credito_reale_bps:
    bps_K_venduta  = K                                               # strike put venduta (calcolato)
    bps_K_comprata = K - larghezza_spread                            # strike put comprata
    bps_credito    = credito_reale_bps                               # credito netto per azione
    bps_credito_tot = round(bps_credito * 100 * n_contratti, 2)      # credito totale
    bps_margine_c  = round((larghezza_spread - bps_credito) * 100, 2) # margine per contratto
    bps_margine_tot = round(bps_margine_c * n_contratti, 2)           # margine totale
    bps_max_profit  = bps_credito_tot                                 # massimo profitto
    bps_max_loss    = bps_margine_tot                                 # massima perdita
    bps_be          = bps_K_venduta - bps_credito                     # break-even
    bps_rend        = (bps_credito_tot / bps_margine_tot * 100) if bps_margine_tot > 0 else 0
    bps_rend_ann    = (((1 + bps_rend / 100) ** 12) - 1) * 100
    bps_pct_largh   = (bps_credito / larghezza_spread) * 100
    bps_tp          = round(bps_credito_tot * 0.5, 2)                # take profit al 50%
    bps_sl          = round(bps_credito_tot * 2, 2)                  # stop loss a 2x
    bps_dist_venduta = (spot - bps_K_venduta) / spot * 100
    bps_dist_comprata = (spot - bps_K_comprata) / spot * 100
    # Deviazione standard a scadenza
    bps_sigma_T     = spot * sigma * np.sqrt(T)
    bps_dist_sd     = (spot - bps_K_venduta) / bps_sigma_T if bps_sigma_T > 0 else 0
    # Semaforo regola 25-35%
    if bps_pct_largh >= 30:
        bps_regola_cls = "ok"; bps_regola_txt = "Credito ottimale (>30%)"
    elif bps_pct_largh >= 25:
        bps_regola_cls = "warn"; bps_regola_txt = "Credito accettabile (25-30%)"
    else:
        bps_regola_cls = "bad"; bps_regola_txt = "Credito insufficiente (<25%) — rischio non efficiente"
else:
    bps_K_venduta = bps_K_comprata = bps_credito = bps_credito_tot = None
    bps_margine_c = bps_margine_tot = bps_max_profit = bps_max_loss = None
    bps_be = bps_rend = bps_rend_ann = bps_pct_largh = bps_tp = bps_sl = None
    bps_dist_venduta = bps_dist_comprata = bps_dist_sd = bps_sigma_T = None
    bps_regola_cls = bps_regola_txt = None

# IV Rank badge
ivr_cls   = "alto" if iv_rank >= 60 else "medio" if iv_rank >= 35 else "basso"
ivr_label = "Alto &mdash; Vendi" if iv_rank >= 60 else "Medio &mdash; Valuta" if iv_rank >= 35 else "Basso &mdash; Aspetta"

# VIX colore
vix_str = fmt(vix_val, 2) if vix_val else "N/D"
vix_cls = "green" if vix_val and vix_val >= 20 else "gold" if vix_val and vix_val >= 15 else "red"


# ═══════════════════════════════════════════════════════════
# RENDER UI
# ═══════════════════════════════════════════════════════════

# ── HEADER ──
strat_header_label = "Vendita Put Scoperta" if STRATEGIA == "put_scoperta" else "Bull Put Spread"
strat_header_icon  = "&#9679;" if STRATEGIA == "put_scoperta" else "&#9670;"
st.markdown(f"""
<div class="ph-header">
    <div style="display:flex;align-items:center;gap:1.2rem">
        <span class="ph-logo">Phinance</span>
        <div style="width:1px;height:2rem;background:var(--border-medium)"></div>
        <span class="ph-subtitle">{strat_header_icon} {strat_header_label} &middot; Motore Black-Scholes</span>
    </div>
    <div class="ph-header-right">
        <span class="ph-tag">v5.1 &middot; Yahoo Finance &middot; CBOE VIX</span>
        <span style="font-family:var(--font-mono);font-size:0.55rem;color:var(--text-muted);letter-spacing:0.1em">SOLO A SCOPO EDUCATIVO</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── BARRA 4 DATI LIVE &mdash; frecce semantiche ──
# Usiamo delta_color="off" su tutti: Streamlit non aggiunge frecce proprie.
# Freccia e colore nel testo, poi CSS custom colora i delta per posizione.

# Prezzo Spot
if var > 0.05:
    spot_arrow = f"&#9650; +{fmt(var,2)}% oggi"
    spot_cls   = "green"
elif var < -0.05:
    spot_arrow = f"&#9660; {fmt(var,2)}% oggi"
    spot_cls   = "red"
else:
    spot_arrow = f"&#8596; {fmt(var,2)}% oggi"
    spot_cls   = "gold"

# Vol. Storica: alta=verde, media=arancio, bassa=rosso
if vol_st >= 25:
    vol_arrow = "&#9650; Alta &mdash; Premi elevati"
    vol_cls   = "green"
elif vol_st >= 15:
    vol_arrow = "&#8596; Media &mdash; Nella norma"
    vol_cls   = "gold"
else:
    vol_arrow = "&#9660; Bassa &mdash; Premi scarsi"
    vol_cls   = "red"

# IV Rank: alto=verde, medio=arancio, basso=rosso
if iv_rank >= 60:
    ivr_arrow = "&#9650; Alto &mdash; Vendi"
    ivr_cls   = "green"
elif iv_rank >= 35:
    ivr_arrow = "&#8596; Medio &mdash; Valuta"
    ivr_cls   = "gold"
else:
    ivr_arrow = "&#9660; Basso &mdash; Aspetta"
    ivr_cls   = "red"

# VIX: alto=verde, medio=arancio, basso=rosso
if vix_val and vix_val >= 20:
    vix_arrow = "&#9650; Elevato &mdash; Buono per vendere"
    vix_cls   = "green"
elif vix_val and vix_val >= 15:
    vix_arrow = "&#8596; Normale &mdash; Nella norma"
    vix_cls   = "gold"
elif vix_val:
    vix_arrow = "&#9660; Basso &mdash; Premi scarsi"
    vix_cls   = "red"
else:
    vix_arrow = "Non disponibile"
    vix_cls   = "gold"


st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;margin-bottom:2rem">

  <div class="kpi-card" style="animation-delay:0.0s">
    <div class="kpi-eyebrow greek-tooltip">&#9679; Prezzo Spot
        <span class="tip-icon">?</span>
        <div class="tip-box">Prezzo di chiusura pi&ugrave; recente del sottostante selezionato, scaricato in tempo reale da Yahoo Finance. &Egrave; il riferimento base per tutti i calcoli di strike, premio e margine.</div>
    </div>
    <div class="kpi-value {spot_cls}" style="font-size:1.9rem">{fmt(spot,2)}</div>
    <div class="kpi-sub">Aggiornato: {ts_spot}</div>
    <div><span class="kpi-badge {spot_cls}">{spot_arrow}</span></div>
  </div>

  <div class="kpi-card" style="animation-delay:0.06s">
    <div class="kpi-eyebrow greek-tooltip">&#9679; Vol. Storica 30gg
        <span class="tip-icon">?</span>
        <div class="tip-box">Volatilità reale del sottostante negli ultimi 30 giorni, annualizzata. Indica quanto si è mosso il prezzo storicamente. Confrontata con la IV: se IV &gt; Vol. Storica significa che le opzioni sono care &mdash; condizione favorevole per vendere.</div>
    </div>
    <div class="kpi-value {vol_cls}" style="font-size:1.9rem">{fmt(vol_st,2)}%</div>
    <div class="kpi-sub">Aggiornato: {ts_vol}</div>
    <div><span class="kpi-badge {vol_cls}">{vol_arrow}</span></div>
  </div>

  <div class="kpi-card" style="animation-delay:0.12s">
    <div class="kpi-eyebrow greek-tooltip">&#9679; IV Rank
        <span class="tip-icon">?</span>
        <div class="tip-box">Indica quanto è alta la volatilità implicita attuale rispetto agli ultimi 12 mesi. 0 = minimo storico, 100 = massimo storico. Sopra 50 = buon momento per vendere opzioni. Sotto 35 = premi troppo bassi, meglio aspettare.</div>
    </div>
    <div class="kpi-value {ivr_cls}" style="font-size:1.9rem">{fmt(iv_rank,0)} / 100</div>
    <div class="kpi-sub">Aggiornato: {ts_ivr}</div>
    <div><span class="kpi-badge {ivr_cls}">{ivr_arrow}</span></div>
  </div>

  <div class="kpi-card" style="animation-delay:0.18s">
    <div class="kpi-eyebrow greek-tooltip">&#9679; VIX &mdash; Indice di Paura
        <span class="tip-icon">?</span>
        <div class="tip-box">Il VIX misura la volatilità implicita attesa sull&apos;S&amp;P 500 nei prossimi 30 giorni. Sotto 15 = mercato tranquillo, premi bassi. 15-20 = normale. Sopra 20 = paura elevata, premi gonfiati &mdash; ottimo per vendere put.</div>
    </div>
    <div class="kpi-value {vix_cls}" style="font-size:1.9rem">{vix_str}</div>
    <div class="kpi-sub">Aggiornato: {ts_vix}</div>
    <div><span class="kpi-badge {vix_cls}">{vix_arrow}</span></div>
  </div>

</div>
""", unsafe_allow_html=True)

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


# ══════════════════════════════════════════════════════════
# DASHBOARD — PUT SCOPERTA
# ══════════════════════════════════════════════════════════
if STRATEGIA == "put_scoperta":

    # ── KPI CARDS &mdash; 4 colonne ──
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="animation-delay:0.0s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Strike Consigliato
                <span class="tip-icon">?</span>
                <div class="tip-box">Lo strike viene calcolato automaticamente con Black-Scholes in base alla probabilit&agrave; di successo che imposti nella sidebar. All&apos;84% corrisponde un delta di circa 0,16 &mdash; il punto ottimale per la strategia.</div>
            </div>
            <div class="kpi-value cyan">{fmt(K,2)}</div>
            <div class="kpi-sub">{fmt(dist,2)}% sotto lo spot</div>
            <div><span class="kpi-badge green">OTM TARGET</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        bc = "green" if prob >= 0.90 else "gold" if prob >= 0.80 else "red"
        bt = "Eccellente" if prob >= 0.90 else "Accettabile" if prob >= 0.80 else "Rischiosa"
        vc = "green"  if prob >= 0.90 else "gold" if prob >= 0.80 else "red"
        st.markdown(f"""
        <div class="kpi-card" style="animation-delay:0.06s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Probabilit&agrave; di Successo
                <span class="tip-icon">?</span>
                <div class="tip-box">Probabilit&agrave; che l&apos;opzione scada OTM e tu incassi il premio intero. Calcolata con Black-Scholes come N(d2). 84% = ottimale per la strategia. Sopra 90% = pi&ugrave; sicuro ma premio molto basso.</div>
            </div>
            <div class="kpi-value {vc}">{fmt(prob*100,2)}%</div>
            <div class="kpi-sub">Scade senza perdite</div>
            <div><span class="kpi-badge {bc}">{bt}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="animation-delay:0.12s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Premio Incassato
                <span class="tip-icon">?</span>
                <div class="tip-box">Il premio &egrave; il massimo guadagno possibile &mdash; lo incassi subito alla vendita. Se l&apos;opzione scade OTM tieni tutto. Strategia comune: chiudi al 50% del profitto riacquistando l&apos;opzione a prezzo inferiore.</div>
            </div>
            <div class="kpi-value green">{fmt(prem,2)}</div>
            <div class="kpi-sub">{n_contratti} contratti &rarr; <strong style="color:var(--accent-green)">+{fmt(ptot,0)} &euro;</strong></div>
            <div><span class="kpi-badge green">{fmt(rend,2)}% sul margine / mese</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card" style="animation-delay:0.18s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Margine Richiesto
                <span class="tip-icon">?</span>
                <div class="tip-box">Il margine &egrave; la liquidit&agrave; che il broker blocca come garanzia. Non &egrave; un costo &mdash; rimane tuo &mdash; ma non puoi usarla per altri trade. Il valore &egrave; una stima: verifica sempre sul tuo broker prima di operare.</div>
            </div>
            <div class="kpi-value gold">{fmt(marg_tot,0)} &euro;</div>
            <div class="kpi-sub">{fmt(mc,0)} &euro; &times; {n_contratti} contratti</div>
            <div><span class="kpi-badge gold">DA AVERE SUL CONTO</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── DETTAGLIO POSIZIONE ──
    _s = "background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:var(--radius-xl);padding:0.9rem 1rem;height:110px;max-height:110px;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between;cursor:default"
    _v = "font-family:'DM Sans',sans-serif;font-weight:700;letter-spacing:-0.03em;white-space:nowrap;overflow:hidden;text-overflow:clip"
    _e = "font-family:'DM Mono',monospace;font-size:0.55rem;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:#3E526A;margin-bottom:0.3rem;white-space:nowrap"
    _b = "font-family:'DM Mono',monospace;font-size:0.6rem;color:#3E526A;white-space:nowrap;overflow:hidden"
    st.markdown("<span style='font-family:var(--font-mono);font-size:0.6rem;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-secondary)'><span style='color:var(--accent-green);margin-right:0.5rem'>&#9678;</span>Dettaglio Posizione <span style='color:var(--text-muted);font-weight:400'>(margine stimato)</span></span>", unsafe_allow_html=True)
    d1,d2,d3,d4,d5,d6 = st.columns(6, gap="small")
    with d1:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Contratti</div><div style="{_v};font-size:1.2rem;color:var(--accent-cyan)">{n_contratti}</div><div style="{_b}">selezionati</div></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Margine / contratto</div><div style="{_v};font-size:1.2rem;color:var(--accent-cyan)">{fmt(mc,2)} &euro;</div><div style="{_b}">{fmt(marg_pct,0)}% × strike</div></div>', unsafe_allow_html=True)
    with d3:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Margine totale</div><div style="{_v};font-size:1.2rem;color:var(--accent-gold)">{fmt(marg_tot,2)} &euro;</div><div style="{_b}">da avere sul conto</div></div>', unsafe_allow_html=True)
    with d4:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Incasso premi</div><div style="{_v};font-size:1.2rem;color:var(--accent-green)">+{fmt(ptot,2)} &euro;</div><div style="{_b}">{n_contratti} × {fmt(prem,2)} × 100</div></div>', unsafe_allow_html=True)
    with d5:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Theta / giorno</div><div style="{_v};font-size:1.2rem;color:var(--accent-green)">+{fmt(thday,2)} &euro;</div><div style="{_b}">guadagno dal tempo</div></div>', unsafe_allow_html=True)
    with d6:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Rendimento</div><div style="{_v};font-size:1.2rem;color:var(--accent-green)">{fmt(rend,2)}% / mese</div><div style="{_b}">{fmt(rend_ann,2)}% / anno</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── GRECHE ──
    delta_display = delta_reale if delta_reale is not None else abs(gre['delta'])
    theta_display = theta_reale if theta_reale is not None else abs(gre['theta']) * 100
    delta_fonte = "Reale (broker)" if delta_reale is not None else "Black-Scholes (stimato)"
    theta_fonte = "Reale (broker)" if theta_reale is not None else "Black-Scholes (stimato)"

    st.markdown(f"""
    <div class="panel" style="animation-delay:0.3s;margin-bottom:1.5rem">
        <div class="panel-title"><span style="color:var(--accent-cyan);margin-right:0.4rem">&#8721;</span> Lettere Greche</div>
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:0">
            <div style="padding:1.2rem 1.8rem;border-right:1px solid rgba(255,255,255,0.04)">
                <div class="panel-key greek-tooltip" style="margin-bottom:0.5rem">
                    &#916; Delta (prob. ITM)
                    <span class="tip-icon">?</span>
                    <div class="tip-box">Misura quanto varia il premio per ogni $1 di movimento del sottostante. In valore assoluto = probabilit&agrave; che l&apos;opzione scada ITM (in perdita). Ottimale: 0.15&ndash;0.20.</div>
                </div>
                <div class="panel-val cyan" style="font-size:1.6rem">{fmt(delta_display,2)}</div>
                <div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--text-secondary);margin-top:0.4rem">{fmt(delta_display*100,1)}% prob. ITM &nbsp;&middot;&nbsp; <span style="color:var(--text-muted)">{delta_fonte}</span></div>
            </div>
            <div style="padding:1.2rem 1.8rem">
                <div class="panel-key greek-tooltip" style="margin-bottom:0.5rem">
                    &#920; Theta (&euro;/giorno)
                    <span class="tip-icon">?</span>
                    <div class="tip-box">Il tuo guadagno quotidiano dal passare del tempo (time decay). Vendendo put incassi theta positivo: ogni giorno che passa il valore dell&apos;opzione diminuisce e tu guadagni. &Egrave; il motore principale della strategia.</div>
                </div>
                <div class="panel-val green" style="font-size:1.6rem">+{fmt(theta_display,2)} &euro;</div>
                <div style="font-family:var(--font-mono);font-size:0.62rem;color:var(--text-secondary);margin-top:0.4rem">guadagno per giorno &nbsp;&middot;&nbsp; <span style="color:var(--text-muted)">{theta_fonte}</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SCENARIO CRISI ──
    st.markdown(f"""
    <div class="crisis-panel" style="animation-delay:0.35s">
        <div class="crisis-header">&#9888; Scenario di Crisi &mdash; Crollo {fmt(sc['crash'],0)}%</div>
        <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0">
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column;justify-content:flex-start">
                <div class="crisis-key" style="margin-bottom:0.6rem;min-height:1.2rem">Prezzo dopo il crollo</div>
                <div class="crisis-val">{fmt(sc['Sc'],2)}</div>
            </div>
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Perdita per contratto</div>
                <div class="crisis-val red">{fmt(sc['lc'],2)} &euro;</div>
            </div>
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Perdita lorda totale</div>
                <div class="crisis-val red">{fmt(sc['lt_gross'],2)} &euro;</div>
            </div>
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Premi gi&agrave; incassati</div>
                <div class="crisis-val green">+{fmt(sc['pt'],2)} &euro;</div>
            </div>
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Perdita netta finale</div>
                <div class="crisis-val red" style="font-size:1rem;font-weight:700">{fmt(pn,0)} &euro;</div>
            </div>
            <div style="padding:0.8rem 1.2rem;display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Impatto sul margine</div>
                <div class="crisis-val red">{fmt(imp,2)}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RIEPILOGO PUT SCOPERTA ──
    st.markdown("<div class='section-label'>Riepilogo Operazione</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Parametro": ["Strumento","Prezzo Attuale","Strike Consigliato","Distanza Strike",
                      "Giorni alla Scadenza","IV Impostata","Vol. Storica 30gg","VIX Corrente","IV Rank",
                      "Premio per Contratto","Numero Contratti","Margine per Contratto",
                      "Margine Totale Richiesto","Incasso Totale Premi",
                      "Punto di Pareggio","Theta Giornaliero","Rendimento sul Margine"],
        "Valore":    [nome, fmt(spot,2), fmt(K,2), f"{fmt(dist,2)}% sotto lo spot",
                      f"{dte} gg", f"{fmt(iv_pct,2)}%", f"{fmt(vol_st,2)}%",
                      vix_str + (" (preimpostato in IV)" if vix_val else ""),
                      f"{fmt(iv_rank,2)}/100 &mdash; {ivr_label}",
                      f"{fmt(prem,4)}  ({fmt(prem*100,2)} &euro; / contratto 100 azioni)",
                      str(n_contratti), f"{fmt(mc,0)} &euro;",
                      f"{fmt(marg_tot,0)} &euro; (da avere sul conto)",
                      f"+{fmt(ptot,0)} &euro;",
                      fmt(K-prem,2), f"+{fmt(thday,2)} &euro; / giorno",
                      f"{fmt(rend,2)}% / mese  ({fmt(rend_ann,2)}% annuo composto stimato)"],
    }), use_container_width=True, hide_index=True,
        column_config={
            "Parametro": st.column_config.TextColumn(width="medium"),
            "Valore":    st.column_config.TextColumn(width="large"),
        })

# ══════════════════════════════════════════════════════════
# DASHBOARD — BULL PUT SPREAD
# ══════════════════════════════════════════════════════════
elif STRATEGIA == "bull_put_spread" and bps_credito_tot is not None:

    # ── KPI CARDS BPS ──
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="animation-delay:0.0s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Strike Venduto
                <span class="tip-icon">?</span>
                <div class="tip-box">Lo strike della put che vendi &mdash; calcolato con Black-Scholes in base alla probabilit&agrave; di successo impostata. Incassi il premio pi&ugrave; alto. Se SPY rimane sopra questo strike a scadenza tieni tutto il credito.</div>
            </div>
            <div class="kpi-value cyan">{fmt(bps_K_venduta,2)}</div>
            <div class="kpi-sub">{fmt(bps_dist_venduta,2)}% sotto lo spot</div>
            <div><span class="kpi-badge green">PUT VENDUTA (STO)</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card" style="animation-delay:0.06s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Strike Comprato
                <span class="tip-icon">?</span>
                <div class="tip-box">Lo strike della put che compri come protezione &mdash; distante {larghezza_spread}$ dalla put venduta. Limita la perdita massima. Se SPY scende sotto questo livello la perdita non aumenta ulteriormente.</div>
            </div>
            <div class="kpi-value gold">{fmt(bps_K_comprata,2)}</div>
            <div class="kpi-sub">{fmt(bps_dist_comprata,2)}% sotto lo spot</div>
            <div><span class="kpi-badge gold">PUT COMPRATA (BTO)</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        cred_cls = "green" if bps_pct_largh >= 30 else "gold" if bps_pct_largh >= 25 else "red"
        st.markdown(f"""
        <div class="kpi-card" style="animation-delay:0.12s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Credito Netto
                <span class="tip-icon">?</span>
                <div class="tip-box">Il credito netto &egrave; la differenza tra il premio incassato e quello pagato. Deve essere almeno il 25-30% della larghezza dello spread ({larghezza_spread}$) per avere un valore atteso positivo. Regola professionale fondamentale.</div>
            </div>
            <div class="kpi-value {cred_cls}">{fmt(bps_credito,2)}</div>
            <div class="kpi-sub">{n_contratti} contratti &rarr; <strong style="color:var(--accent-green)">+{fmt(bps_credito_tot,0)} &euro;</strong></div>
            <div><span class="kpi-badge {cred_cls}">{fmt(bps_pct_largh,1)}% della larghezza</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card" style="animation-delay:0.18s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Margine Fisso
                <span class="tip-icon">?</span>
                <div class="tip-box">Il margine del bull put spread &egrave; fisso e predefinito: (larghezza &mdash; credito) &times; 100. Non varia con il prezzo del sottostante. &Egrave; anche la perdita massima teorica assoluta della posizione.</div>
            </div>
            <div class="kpi-value gold">{fmt(bps_margine_tot,0)} &euro;</div>
            <div class="kpi-sub">{fmt(bps_margine_c,0)} &euro; &times; {n_contratti} contratti</div>
            <div><span class="kpi-badge gold">FISSO &mdash; RISCHIO DEFINITO</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── DETTAGLIO POSIZIONE BPS ──
    _s = "background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:var(--radius-xl);padding:0.9rem 1rem;height:110px;max-height:110px;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between;cursor:default"
    _v = "font-family:'DM Sans',sans-serif;font-weight:700;letter-spacing:-0.03em;white-space:nowrap;overflow:hidden;text-overflow:clip"
    _e = "font-family:'DM Mono',monospace;font-size:0.55rem;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:#3E526A;margin-bottom:0.3rem;white-space:nowrap"
    _b = "font-family:'DM Mono',monospace;font-size:0.6rem;color:#3E526A;white-space:nowrap;overflow:hidden"
    bps_thday = theta_reale if theta_reale is not None else abs(gre['theta']) * 100
    st.markdown("<span style='font-family:var(--font-mono);font-size:0.6rem;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-secondary)'><span style='color:var(--accent-green);margin-right:0.5rem'>&#9678;</span>Dettaglio Posizione</span>", unsafe_allow_html=True)
    d1,d2,d3,d4,d5 = st.columns(5, gap="small")
    with d1:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Contratti</div><div style="{_v};font-size:1.2rem;color:var(--accent-cyan)">{n_contratti}</div><div style="{_b}">selezionati</div></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Strike venduto</div><div style="{_v};font-size:1.2rem;color:var(--accent-cyan)">{fmt(bps_K_venduta,2)}</div><div style="{_b}">put venduta (STO)</div></div>', unsafe_allow_html=True)
    with d3:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Strike comprato</div><div style="{_v};font-size:1.2rem;color:var(--accent-gold)">{fmt(bps_K_comprata,2)}</div><div style="{_b}">put comprata (BTO)</div></div>', unsafe_allow_html=True)
    with d4:
        cred_col = "var(--accent-green)" if bps_pct_largh >= 30 else "var(--accent-gold)" if bps_pct_largh >= 25 else "var(--accent-red)"
        st.markdown(f'<div style="{_s}"><div style="{_e}">Credito netto</div><div style="{_v};font-size:1.2rem;color:{cred_col}">+{fmt(bps_credito_tot,2)} &euro;</div><div style="{_b}">{fmt(bps_pct_largh,1)}% della larghezza</div></div>', unsafe_allow_html=True)
    with d5:
        st.markdown(f'<div style="{_s}"><div style="{_e}">Margine fisso</div><div style="{_v};font-size:1.2rem;color:var(--accent-gold)">{fmt(bps_margine_tot,2)} &euro;</div><div style="{_b}">rischio definito</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── PANNELLO ANALISI SPREAD ──
    sd_label = f"{fmt(bps_dist_sd,2)} SD" if bps_dist_sd else "N/D"
    be_dist  = (spot - bps_be) / spot * 100
    st.markdown(f"""
    <div class="spread-analysis">
        <div class="spread-analysis-title">&#9670; Analisi Spread &mdash; Bull Put Spread {fmt(bps_K_venduta,0)} / {fmt(bps_K_comprata,0)}</div>
        <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:1rem">
            <div>
                <div class="panel-key" style="margin-bottom:0.3rem">Larghezza</div>
                <div class="panel-val cyan" style="font-size:1.1rem">${larghezza_spread}</div>
            </div>
            <div>
                <div class="panel-key" style="margin-bottom:0.3rem">Break-even</div>
                <div class="panel-val" style="font-size:1.1rem">{fmt(bps_be,2)}</div>
                <div style="font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted)">{fmt(be_dist,2)}% sotto spot</div>
            </div>
            <div>
                <div class="panel-key" style="margin-bottom:0.3rem">Distanza in SD</div>
                <div class="panel-val" style="font-size:1.1rem">{sd_label}</div>
                <div style="font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted)">dal strike venduto</div>
            </div>
            <div>
                <div class="panel-key" style="margin-bottom:0.3rem">Take Profit 50%</div>
                <div class="panel-val green" style="font-size:1.1rem">+{fmt(bps_tp,0)} &euro;</div>
                <div style="font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted)">chiudi qui</div>
            </div>
            <div>
                <div class="panel-key" style="margin-bottom:0.3rem">Stop Loss 2x</div>
                <div class="panel-val red" style="font-size:1.1rem">-{fmt(bps_sl,0)} &euro;</div>
                <div style="font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted)">perdita max gestita</div>
            </div>
            <div>
                <div class="panel-key" style="margin-bottom:0.3rem">Rendimento</div>
                <div class="panel-val green" style="font-size:1.1rem">{fmt(bps_rend,1)}%</div>
                <div style="font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted)">sul margine / mese</div>
            </div>
        </div>
        <div style="margin-top:1rem">
            <span class="spread-rule {bps_regola_cls}">{bps_regola_txt} &mdash; {fmt(bps_pct_largh,1)}% della larghezza ${larghezza_spread}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SCENARIO CRISI BPS (perdita limitata alla larghezza) ──
    bps_crisi_spot = spot * (1 - crash / 100)
    bps_crisi_loss = -bps_margine_tot  # perdita max = margine fisso
    bps_crisi_pct  = (bps_margine_tot / bps_margine_tot * 100) if bps_margine_tot > 0 else 100
    st.markdown(f"""
    <div class="crisis-panel" style="animation-delay:0.35s">
        <div class="crisis-header">&#9888; Scenario di Crisi &mdash; Crollo {fmt(crash,0)}%</div>
        <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0">
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Prezzo dopo il crollo</div>
                <div class="crisis-val">{fmt(bps_crisi_spot,2)}</div>
            </div>
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Strike venduto</div>
                <div class="crisis-val">{fmt(bps_K_venduta,2)}</div>
            </div>
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Strike comprato</div>
                <div class="crisis-val green">{fmt(bps_K_comprata,2)}</div>
            </div>
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Credito incassato</div>
                <div class="crisis-val green">+{fmt(bps_credito_tot,2)} &euro;</div>
            </div>
            <div style="padding:0.8rem 1.2rem;border-right:1px solid rgba(255,90,90,0.08);display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Perdita massima</div>
                <div class="crisis-val red" style="font-size:1rem;font-weight:700">{fmt(bps_crisi_loss,0)} &euro;</div>
            </div>
            <div style="padding:0.8rem 1.2rem;display:flex;flex-direction:column">
                <div class="crisis-key" style="margin-bottom:0.6rem">Perdita limitata a</div>
                <div class="crisis-val green">${larghezza_spread} per azione</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RIEPILOGO BPS ──
    st.markdown("<div class='section-label'>Riepilogo Operazione &mdash; Bull Put Spread</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Parametro": ["Strumento","Prezzo Attuale","Strike Venduto (STO)","Strike Comprato (BTO)",
                      "Larghezza Spread","Giorni alla Scadenza","IV Impostata","VIX Corrente","IV Rank",
                      "Credito Netto per Azione","Credito come % Larghezza","Numero Contratti",
                      "Margine per Contratto (fisso)","Margine Totale Richiesto",
                      "Credito Totale Incassato","Break-even","Take Profit (50%)",
                      "Stop Loss (2x credito)","Rendimento sul Margine"],
        "Valore":    [nome, fmt(spot,2), fmt(bps_K_venduta,2), fmt(bps_K_comprata,2),
                      f"${larghezza_spread}", f"{dte} gg", f"{fmt(iv_pct,2)}%",
                      vix_str, f"{fmt(iv_rank,2)}/100",
                      f"{fmt(bps_credito,4)} ({fmt(bps_credito*100,2)} &euro; / contratto)",
                      f"{fmt(bps_pct_largh,1)}% &mdash; {bps_regola_txt}",
                      str(n_contratti), f"{fmt(bps_margine_c,0)} &euro;",
                      f"{fmt(bps_margine_tot,0)} &euro; (da avere sul conto)",
                      f"+{fmt(bps_credito_tot,0)} &euro;",
                      fmt(bps_be,2), f"+{fmt(bps_tp,0)} &euro;",
                      f"-{fmt(bps_sl,0)} &euro;",
                      f"{fmt(bps_rend,2)}% / mese  ({fmt(bps_rend_ann,2)}% annuo stimato)"],
    }), use_container_width=True, hide_index=True,
        column_config={
            "Parametro": st.column_config.TextColumn(width="medium"),
            "Valore":    st.column_config.TextColumn(width="large"),
        })

elif STRATEGIA == "bull_put_spread":
    st.info("Inserisci il credito netto e la larghezza dello spread nella sidebar per visualizzare l'analisi.")

# ── FOOTER ──
st.markdown("""
<div class="ph-footer">
    <span style="font-size:0.72rem;color:var(--text-secondary);font-weight:500">Phinance</span><br>
    Sistemi Quantitativi per il Trading di Opzioni &middot; v5.0<br>
    Dati: Yahoo Finance &nbsp;&middot;&nbsp; VIX: CBOE &nbsp;&middot;&nbsp; Motore: Black-Scholes<br>
    <span style="color:rgba(255,255,255,0.03);font-size:0.5rem">&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;</span><br>
    Solo a scopo educativo &middot; Non costituisce consulenza finanziaria
</div>
""", unsafe_allow_html=True)
