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
import io

try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable, PageBreak)
    from reportlab.pdfgen import canvas as rl_canvas
    REPORTLAB_OK = True
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "-q"])
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle, HRFlowable, PageBreak)
        from reportlab.pdfgen import canvas as rl_canvas
        REPORTLAB_OK = True
    except ImportError:
        REPORTLAB_OK = False

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
    left: 50%;
    transform: translateX(-50%);
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

def genera_pdf_scenari(strategia, params):
    """
    Genera un PDF con UN unico scenario completo spot -10% → +10%,
    50 prezzi, valori BS a T residuo = DTE/2.
    """
    if not REPORTLAB_OK:
        return None

    # ── Estrai parametri ─────────────────────────────────────────────────────
    spot      = params["spot"]
    sigma     = params["sigma"]
    T         = params["T"]
    r         = params["r"]
    nome      = params["nome"]
    dte       = params["dte"]
    data_oggi = datetime.now().strftime("%d/%m/%Y")

    if strategia == "put_scoperta":
        K      = params["K"]
        prem   = params["prem"]
        n      = params["n_contratti"]
        mult   = 100
        K_ref  = K
    else:
        K_v    = params["bps_K_venduta"]
        K_c    = params["bps_K_comprata"]
        credito= params["bps_credito"]
        n      = params["n_contratti"]
        mult   = 100
        pv_reale = params.get("prezzo_put_venduta")
        pc_reale = params.get("prezzo_put_comprata")
        K_ref  = K_v

    # ── Monte Carlo per sintesi statistica (pagina 1) ────────────────────────
    np.random.seed(42)
    prezzi_sim = spot * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*np.random.standard_normal(10000))
    p75 = float(np.percentile(prezzi_sim, 75))
    p50 = float(np.percentile(prezzi_sim, 50))
    p10 = float(np.percentile(prezzi_sim, 10))
    pct_pos = float(np.mean(prezzi_sim > K_ref)) * 100
    pct_neg = 100 - pct_pos

    T_residuo = max(T * 0.5, 1/365)

    def bs_put_price(S, K_opt, T_opt, r_opt, sig):
        if T_opt <= 0 or S <= 0:
            return max(K_opt - S, 0)
        from scipy.stats import norm as _norm
        d1 = (np.log(S/K_opt) + (r_opt + 0.5*sig**2)*T_opt) / (sig*np.sqrt(T_opt))
        d2 = d1 - sig*np.sqrt(T_opt)
        return max(round(K_opt*np.exp(-r_opt*T_opt)*_norm.cdf(-d2) - S*_norm.cdf(-d1), 2), 0.0)

    # ── Setup ReportLab ───────────────────────────────────────────────────────
    buf = io.BytesIO()
    W, H = A4

    # Palette — testi fuori tabella su sfondo scuro
    BG      = colors.HexColor("#080C10")
    CYAN    = colors.HexColor("#00C2FF")
    GREEN   = colors.HexColor("#00E5A0")
    GOLD    = colors.HexColor("#FFB547")
    RED     = colors.HexColor("#FF5A5A")
    MUTED   = colors.HexColor("#8B9FC0")
    SURFACE = colors.HexColor("#0F1E2E")
    BORDER  = colors.HexColor("#243550")
    WHITE   = colors.HexColor("#E8EDF5")
    DARK    = colors.HexColor("#060A0E")
    TEXT    = colors.HexColor("#C8D4E8")   # testo leggibile su sfondo scuro

    strat_label = "Vendita Put Scoperta" if strategia == "put_scoperta" else "Bull Put Spread"

    def on_page(canv, doc):
        canv.saveState()
        # Sfondo scuro sull'intera pagina
        canv.setFillColor(BG)
        canv.rect(0, 0, W, H, fill=1, stroke=0)
        # Header band
        canv.setFillColor(DARK)
        canv.rect(0, H - 1.6*cm, W, 1.6*cm, fill=1, stroke=0)
        canv.setFont("Helvetica-Bold", 12)
        canv.setFillColor(CYAN)
        canv.drawString(1.5*cm, H - 1.05*cm, "Phinance")
        canv.setFont("Helvetica", 8)
        canv.setFillColor(WHITE)
        canv.drawString(4.2*cm, H - 1.05*cm, f"| Analisi Scenari — {strat_label}")
        canv.setFillColor(MUTED)
        canv.drawRightString(W - 1.5*cm, H - 1.05*cm, data_oggi)
        canv.setStrokeColor(BORDER)
        canv.setLineWidth(0.5)
        canv.line(1.5*cm, H - 1.6*cm, W - 1.5*cm, H - 1.6*cm)
        # Footer
        canv.setFont("Helvetica", 7)
        canv.setFillColor(MUTED)
        canv.drawCentredString(W/2, 0.65*cm,
            "Solo a scopo educativo — non costituisce consulenza finanziaria — Phinance v5.1")
        canv.line(1.5*cm, 1.05*cm, W - 1.5*cm, 1.05*cm)
        canv.restoreState()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.4*cm, bottomMargin=1.8*cm,
    )

    def ps(name, font="Helvetica", size=9, color=None, align=TA_LEFT,
           leading=None, spaceBefore=0, spaceAfter=0):
        c = color if color is not None else TEXT
        return ParagraphStyle(name, fontName=font, fontSize=size,
                              textColor=c, alignment=align,
                              leading=leading or size*1.4,
                              spaceBefore=spaceBefore, spaceAfter=spaceAfter)

    s_title   = ps("title", "Helvetica-Bold", 18, CYAN,  TA_LEFT, spaceAfter=4)
    s_sub     = ps("sub",   "Helvetica",       9, MUTED, TA_LEFT, spaceAfter=2)
    s_h2      = ps("h2",    "Helvetica-Bold", 11, CYAN,  TA_LEFT, spaceBefore=8, spaceAfter=4)
    s_body    = ps("body",  "Helvetica",       8, TEXT,  TA_LEFT, leading=13, spaceAfter=3)
    s_nota    = ps("nota",  "Helvetica",       7, MUTED, TA_LEFT, leading=11, spaceAfter=3)
    s_comment = ps("comm",  "Helvetica",       8, TEXT,  TA_LEFT, leading=12)

    story = []

    # ═══════════════════════════════════════════════════════
    # PAGINA 1 — INTRO + PARAMETRI + STATISTICHE
    # ═══════════════════════════════════════════════════════
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Analisi Scenari — Report Operativo", s_title))
    story.append(Paragraph(f"{nome}  ·  {strat_label}  ·  Generato il {data_oggi}", s_sub))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 0.35*cm))

    story.append(Paragraph(
        "Questo report analizza la posizione su una fascia <b>\u221210% / +10%</b> rispetto allo spot, "
        "con 30 livelli equidistanti. Valori calcolati con <b>Black-Scholes</b> a T residuo = DTE/2.",
        s_body))
    story.append(Paragraph(
        "Il P&L include il credito gi\xe0 incassato. Solo a scopo educativo — non costituisce consulenza finanziaria.",
        s_nota))
    story.append(Spacer(1, 0.3*cm))

    # ── Tabella parametri ────────────────────────────────────────────────────
    story.append(Paragraph("Parametri operazione", s_h2))
    if strategia == "put_scoperta":
        param_rows = [
            ["Strumento",   nome,          "Strike",           f"{K:.2f}"],
            ["Prezzo Spot", f"{spot:.2f}", "Premio / az.",     f"{prem:.4f}"],
            ["DTE",         f"{dte} gg",   "Contratti",        str(n)],
            ["IV",          f"{sigma*100:.1f}%", "Credito tot.", f"+{prem*n*mult:.0f} \u20ac"],
        ]
    else:
        pv_str = f"{pv_reale:.2f}" if pv_reale else f"{credito:.4f}"
        pc_str = f"{pc_reale:.2f}" if pc_reale else "\u2014"
        param_rows = [
            ["Strumento",    nome,              "Strike vend.",     f"{K_v:.2f}"],
            ["Prezzo Spot",  f"{spot:.2f}",     "Strike comp.",     f"{K_c:.2f}"],
            ["DTE",          f"{dte} gg",       "Put vend. (bid)",  pv_str],
            ["IV",           f"{sigma*100:.1f}%","Put comp. (ask)", pc_str],
            ["Contratti",    str(n),            "Credito netto",    f"{credito:.2f} (+{credito*n*mult:.0f}\u20ac)"],
        ]

    total_w = W - 3*cm
    col_w4  = [total_w*0.20, total_w*0.30, total_w*0.24, total_w*0.26]
    param_style = TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), SURFACE),
        ("GRID",        (0,0), (-1,-1), 0.3, BORDER),
        ("FONTNAME",    (0,0), (0,-1),  "Helvetica-Bold"),
        ("FONTNAME",    (2,0), (2,-1),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("TEXTCOLOR",   (0,0), (0,-1),  MUTED),
        ("TEXTCOLOR",   (2,0), (2,-1),  MUTED),
        ("TEXTCOLOR",   (1,0), (1,-1),  WHITE),
        ("TEXTCOLOR",   (3,0), (3,-1),  CYAN),
        ("PADDING",     (0,0), (-1,-1), 6),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("WORDWRAP",    (0,0), (-1,-1), True),
    ])
    story.append(Table(param_rows, colWidths=col_w4, style=param_style))
    story.append(Spacer(1, 0.3*cm))

    # ── Sintesi statistica ───────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.3, color=BORDER))
    story.append(Paragraph("Sintesi statistica", s_h2))
    stat_rows = [
        ["Prezzo mediano",      f"{p50:.2f}",  "Prob. sopra strike",   f"{pct_pos:.1f}%  \u2713"],
        ["P75\xb0 percentile",  f"{p75:.2f}",  "Prob. sotto strike",   f"{pct_neg:.1f}%  \u2717"],
        ["P10\xb0 percentile",  f"{p10:.2f}",  "Dev. std. simulata",   f"{float(np.std(prezzi_sim)):.2f}"],
    ]
    stat_style = TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), SURFACE),
        ("GRID",        (0,0), (-1,-1), 0.3, BORDER),
        ("FONTNAME",    (0,0), (0,-1),  "Helvetica-Bold"),
        ("FONTNAME",    (2,0), (2,-1),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("TEXTCOLOR",   (0,0), (0,-1),  MUTED),
        ("TEXTCOLOR",   (2,0), (2,-1),  MUTED),
        ("TEXTCOLOR",   (1,0), (1,-1),  CYAN),
        ("TEXTCOLOR",   (3,0), (3,0),   GREEN),
        ("TEXTCOLOR",   (3,1), (3,1),   RED),
        ("TEXTCOLOR",   (3,2), (3,2),   WHITE),
        ("PADDING",     (0,0), (-1,-1), 6),
    ])
    story.append(Table(stat_rows, colWidths=col_w4, style=stat_style))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # PAGINA 2 — SCENARIO UNICO spot -10% → +10% (30 righe)
    # ═══════════════════════════════════════════════════════
    prezzi_sc = list(np.linspace(spot * 0.90, spot * 1.10, 30))  # 30 righe

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Scenario Completo: Spot \u221210% \u2192 +10%", ps(
        "sc_title", "Helvetica-Bold", 13, CYAN, TA_LEFT, spaceAfter=2)))
    story.append(Paragraph(
        f"Fascia: <b>{spot*0.90:.2f} \u2013 {spot*1.10:.2f}</b>  \u00b7  30 livelli  \u00b7  "
        f"BS a T residuo: <b>{max(int(T*365*0.5), 1)} gg</b>  \u00b7  IV: <b>{sigma*100:.1f}%</b>",
        ps("sc_sub", "Helvetica", 8, MUTED, TA_LEFT, spaceAfter=4)))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 0.2*cm))

    # Costruisci righe tabella
    if strategia == "put_scoperta":
        header = ["Prezzo", "Val. Put", "P&L / az.", "P&L Tot. (\u20ac)", "Esito"]
    else:
        header = ["Prezzo", "Put Vend.", "Put Comp.", "Spread", "P&L / az.", "P&L Tot. (\u20ac)", "Esito"]

    rows = [header]
    for sp in prezzi_sc:
        if strategia == "put_scoperta":
            vp     = bs_put_price(sp, K, T_residuo, r, sigma)
            pnl_az = round(prem - vp, 2)
            pnl_t  = round(pnl_az * n * mult, 0)
            esito  = "\u2713 Prof." if pnl_t >= 0 else "\u2717 Perd."
            rows.append([f"{sp:.2f}", f"{vp:.2f}", f"{pnl_az:+.2f}", f"{pnl_t:+.0f}", esito])
        else:
            vv     = bs_put_price(sp, K_v, T_residuo, r, sigma)
            vc     = bs_put_price(sp, K_c, T_residuo, r, sigma)
            vspr   = round(vv - vc, 2)
            pnl_az = round(credito - vspr, 2)
            pnl_t  = round(pnl_az * n * mult, 0)
            esito  = "\u2713 Prof." if pnl_t >= 0 else "\u2717 Perd."
            rows.append([f"{sp:.2f}", f"{vv:.2f}", f"{vc:.2f}", f"{vspr:.2f}",
                         f"{pnl_az:+.2f}", f"{pnl_t:+.0f}", esito])

    if strategia == "put_scoperta":
        cw = [total_w*0.19, total_w*0.17, total_w*0.19, total_w*0.22, total_w*0.23]
    else:
        cw = [total_w*0.14, total_w*0.12, total_w*0.12, total_w*0.12,
              total_w*0.14, total_w*0.17, total_w*0.19]

    tbl_style = [
        ("BACKGROUND",    (0,0),  (-1,0),  SURFACE),
        ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),  (-1,0),  7),
        ("TEXTCOLOR",     (0,0),  (-1,0),  CYAN),
        ("ALIGN",         (0,0),  (-1,0),  "CENTER"),
        ("BOTTOMPADDING", (0,0),  (-1,0),  4),
        ("TOPPADDING",    (0,0),  (-1,0),  4),
        ("FONTNAME",      (0,1),  (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),  (-1,-1), 7),
        ("TEXTCOLOR",     (0,1),  (-1,-1), WHITE),
        ("ALIGN",         (1,1),  (-1,-1), "RIGHT"),
        ("ALIGN",         (0,1),  (0,-1),  "CENTER"),
        ("ALIGN",         (-1,1), (-1,-1), "CENTER"),
        ("GRID",          (0,0),  (-1,-1), 0.25, BORDER),
        ("ROWBACKGROUNDS",(0,1),  (-1,-1), [BG, SURFACE]),
        ("TOPPADDING",    (0,1),  (-1,-1), 2),
        ("BOTTOMPADDING", (0,1),  (-1,-1), 2),
        ("TEXTCOLOR",     (0,1),  (0,-1),  CYAN),
        ("FONTNAME",      (0,1),  (0,-1),  "Helvetica-Bold"),
    ]

    for i, row in enumerate(rows[1:], start=1):
        clr_e = GREEN if "\u2713" in row[-1] else RED
        clr_p = GREEN if "+" in row[-2] else RED
        tbl_style.append(("TEXTCOLOR", (-1, i), (-1, i), clr_e))
        tbl_style.append(("FONTNAME",  (-1, i), (-1, i), "Helvetica-Bold"))
        tbl_style.append(("TEXTCOLOR", (-2, i), (-2, i), clr_p))
        tbl_style.append(("FONTNAME",  (-2, i), (-2, i), "Helvetica-Bold"))

    story.append(Table(rows, colWidths=cw, style=TableStyle(tbl_style), repeatRows=1))
    story.append(Spacer(1, 0.3*cm))

    # Break-even: interpolazione lineare sul cambio di segno del P&L Tot nella tabella
    # rows[1:] = righe dati, colonna P&L Tot = indice -2 (penultima, prima di Esito)
    be_str = "n.d."
    for i in range(len(rows) - 2):  # rows[1] = prima riga dati
        row_a = rows[i + 1]
        row_b = rows[i + 2]
        try:
            pnl_a = float(row_a[-2])
            pnl_b = float(row_b[-2])
            s_a   = float(row_a[0])
            s_b   = float(row_b[0])
        except (ValueError, IndexError):
            continue
        if pnl_a * pnl_b < 0:  # cambio di segno preciso
            be = s_a + (s_b - s_a) * (-pnl_a) / (pnl_b - pnl_a)
            be_str = f"{be:.2f}"
            break
        elif pnl_a == 0:
            be_str = f"{s_a:.2f}"
            break

    n_prof = sum(1 for row in rows[1:] if "\u2713" in row[-1])
    if strategia == "put_scoperta":
        perdita_max = f"{-(K - prem)*n*mult:.0f} \u20ac (teorica)"
    else:
        perdita_max = f"{-(K_v-K_c-credito)*n*mult:.0f} \u20ac"

    story.append(Paragraph(
        f"<b>Riepilogo:</b> {n_prof}/30 livelli in profitto, {30-n_prof} in perdita.  "
        f"Break-even: <b>{be_str}</b>  \u00b7  Perdita max: <b>{perdita_max}</b>.",
        s_comment))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.getvalue()


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
    r_pct = 4.5  # tasso risk-free fisso

    st.markdown("<div class='sb-section'>Posizione & Rischio</div>", unsafe_allow_html=True)
    n_contratti = st.slider("Numero di Contratti", 1, 50, 3,
        help="Quanti contratti vuoi vendere.\nOgni contratto copre 100 azioni del sottostante.")
    marg_pct = st.slider("Margine Broker (%)", 5.0, 50.0, 15.0, 1.0,
        help="% del valore dello strike bloccata come garanzia dal broker.\nIl broker tipicamente richiede il 15-20% per le put OTM su ETF.\nVerifica nelle impostazioni del tuo conto.")
    crash = 20.0  # scenario crisi fisso (usato internamente per calc_wcs)

    st.markdown("<div class='sb-section'>Obiettivo Strategia</div>", unsafe_allow_html=True)
    prob_t = st.slider("Probabilità di Successo (%)", 70.0, 99.0, 84.0, 1.0,
        help="84% = Delta 0.16 — punto ottimale per la strategia.\n90% = Delta 0.10 — più conservativo.\n80% = Delta 0.20 — più aggressivo.")

    # Parametri specifici Bull Put Spread
    if STRATEGIA == "bull_put_spread":
        st.markdown("<div class='sb-section'>Parametri Spread</div>", unsafe_allow_html=True)

        # Prezzo put venduta
        st.markdown("<span style='font-family:var(--font-mono);font-size:0.6rem;color:var(--text-muted);letter-spacing:0.1em'>PUT VENDUTA — prezzo bid ($)</span>", unsafe_allow_html=True)
        def _sync_pv_slider(): st.session_state["_pv_val"] = st.session_state["slider_pv"]
        def _sync_pv_input():  st.session_state["_pv_val"] = st.session_state["input_pv"]
        if "_pv_val" not in st.session_state: st.session_state["_pv_val"] = 2.50
        cur_pv = float(st.session_state["_pv_val"])
        col_pv_s, col_pv_n = st.columns([2,1])
        with col_pv_s:
            st.slider("pv slider", 0.01, 200.0, min(cur_pv, 200.0), 0.01,
                label_visibility="collapsed", key="slider_pv", on_change=_sync_pv_slider)
        with col_pv_n:
            st.number_input("pv input", 0.01, 200.0, min(cur_pv, 200.0), 0.01,
                label_visibility="collapsed", key="input_pv", format="%.2f", on_change=_sync_pv_input)
        prezzo_put_venduta = float(st.session_state["_pv_val"])

        # Prezzo put comprata
        st.markdown("<span style='font-family:var(--font-mono);font-size:0.6rem;color:var(--text-muted);letter-spacing:0.1em'>PUT COMPRATA — prezzo ask ($)</span>", unsafe_allow_html=True)
        def _sync_pc_slider(): st.session_state["_pc_val"] = st.session_state["slider_pc"]
        def _sync_pc_input():  st.session_state["_pc_val"] = st.session_state["input_pc"]
        if "_pc_val" not in st.session_state: st.session_state["_pc_val"] = 1.12
        cur_pc = float(st.session_state["_pc_val"])
        col_pc_s, col_pc_n = st.columns([2,1])
        with col_pc_s:
            st.slider("pc slider", 0.01, 200.0, min(cur_pc, 200.0), 0.01,
                label_visibility="collapsed", key="slider_pc", on_change=_sync_pc_slider)
        with col_pc_n:
            st.number_input("pc input", 0.01, 200.0, min(cur_pc, 200.0), 0.01,
                label_visibility="collapsed", key="input_pc", format="%.2f", on_change=_sync_pc_input)
        prezzo_put_comprata = float(st.session_state["_pc_val"])

        # Larghezza spread
        larghezza_spread = st.select_slider("Larghezza Spread ($)",
            options=[5, 10, 15, 20, 25, 30, 50], value=10,
            help="Differenza in dollari tra lo strike venduto e quello comprato.")

        # Credito netto calcolato automaticamente — nessun display aggiuntivo
        credito_reale_bps = max(0.01, round(prezzo_put_venduta - prezzo_put_comprata, 2))
        st.session_state["_credito_bps"] = credito_reale_bps
    else:
        larghezza_spread = None
        credito_reale_bps = None
        prezzo_put_venduta = None
        prezzo_put_comprata = None

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


    # ── PULSANTE GENERA PDF ──────────────────────────────────────────────────
    st.markdown("<div class='sb-section'>Analisi Scenari</div>", unsafe_allow_html=True)
    genera_pdf_btn = st.button("📄 Genera Report Scenari PDF",
        use_container_width=True,
        help="Genera un PDF scaricabile con l'analisi completa della posizione su una fascia -10%/+10% dallo spot, "
             "25 prezzi ciascuno con valore delle opzioni e P&L a scadenza.")


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

# POP Bull Put Spread calcolato dopo i calcoli BPS
pop_bps = None
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
    # POP Bull Put Spread: N(d2_venduta) - N(d2_comprata)
    par_v  = Par(S=spot, K=bps_K_venduta,  T=T, r=r, sigma=sigma)
    par_c  = Par(S=spot, K=bps_K_comprata, T=T, r=r, sigma=sigma)
    _, d2_v = d1d2(par_v)
    _, d2_c = d1d2(par_c)
    pop_bps = round((si.norm.cdf(d2_v) - si.norm.cdf(d2_c)) * 100, 2)
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
# GENERA PDF SE RICHIESTO
# ═══════════════════════════════════════════════════════════
if genera_pdf_btn:
    pdf_params = {
        "spot": spot, "sigma": sigma, "T": T, "r": r,
        "nome": nome, "dte": dte, "n_contratti": n_contratti,
        "K": K, "prem": prem,
        "bps_K_venduta": bps_K_venduta, "bps_K_comprata": bps_K_comprata,
        "bps_credito": bps_credito,
        "bps_be": bps_be,
        "prezzo_put_venduta": prezzo_put_venduta if STRATEGIA == "bull_put_spread" else None,
        "prezzo_put_comprata": prezzo_put_comprata if STRATEGIA == "bull_put_spread" else None,
    }
    with st.spinner("Generazione report PDF in corso…"):
        pdf_bytes = genera_pdf_scenari(STRATEGIA, pdf_params)
    if pdf_bytes:
        ticker_clean = tk.replace("^", "").upper()
        fname = f"phinance_scenari_{ticker_clean}_{datetime.now().strftime('%Y%m%d')}.pdf"
        st.sidebar.download_button(
            label="⬇️ Scarica il PDF",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
        )
        st.sidebar.success("Report pronto! Clicca per scaricare.")
    else:
        st.sidebar.error("Errore nella generazione del PDF. Verifica che reportlab sia installato.")

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

    # ── RIEPILOGO PUT SCOPERTA ──
    st.markdown("<div class='section-label'>Riepilogo Operazione</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Parametro": ["Strumento","Prezzo Attuale","Strike Consigliato","Distanza Strike",
                      "Giorni alla Scadenza",
                      "Premio per Contratto","Numero Contratti","Margine per Contratto",
                      "Margine Totale Richiesto","Incasso Totale Premi",
                      "Punto di Pareggio","Theta Giornaliero","Rendimento sul Margine"],
        "Valore":    [nome, fmt(spot,2), fmt(K,2), f"{fmt(dist,2)}% sotto lo spot",
                      f"{dte} gg",
                      f"{fmt(prem,4)}  ({fmt(prem*100,2)} € / contratto 100 azioni)",
                      str(n_contratti), f"{fmt(mc,0)} €",
                      f"{fmt(marg_tot,0)} € (da avere sul conto)",
                      f"+{fmt(ptot,0)} €",
                      fmt(K-prem,2), f"+{fmt(thday,2)} € / giorno",
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

    # ── POP CARD — BULL PUT SPREAD ──
    pop_bps_cls   = "green" if pop_bps >= 70 else "gold" if pop_bps >= 60 else "red"
    pop_bps_badge = "ECCELLENTE" if pop_bps >= 75 else "OTTIMALE" if pop_bps >= 70 else "ACCETTABILE" if pop_bps >= 60 else "RISCHIOSA"
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 2fr;gap:2rem;margin-bottom:0.5rem">
        <div class="kpi-card" style="animation-delay:0.24s">
            <div class="kpi-eyebrow greek-tooltip">&#9679; Probability of Profit (POP)
                <span class="tip-icon">?</span>
                <div class="tip-box">Per il Bull Put Spread il POP &egrave; la probabilit&agrave; che il prezzo resti sopra entrambi gli strike a scadenza. Formula: N(d2 strike venduto) &minus; N(d2 strike comprato). Tipicamente pi&ugrave; bassa della put scoperta perch&eacute; la finestra di profitto &egrave; pi&ugrave; stretta.</div>
            </div>
            <div class="kpi-value {pop_bps_cls}" style="font-size:2.2rem">{fmt(pop_bps,1)}%</div>
            <div class="kpi-sub">probabilit&agrave; spread scade OTM</div>
            <div><span class="kpi-badge {pop_bps_cls}">{pop_bps_badge}</span></div>
        </div>
        <div class="kpi-card" style="animation-delay:0.30s;background:rgba(0,194,255,0.02)">
            <div class="panel-title" style="font-size:0.58rem;margin-bottom:0.8rem"><span style="color:var(--accent-cyan);margin-right:0.4rem">&#9432;</span>Come leggere il POP sul Bull Put Spread</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem">
                <div>
                    <div style="font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem">POP &ge; 75%</div>
                    <div style="font-family:var(--font-body);font-size:0.82rem;color:var(--accent-green);font-weight:600">Eccellente</div>
                    <div style="font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted)">Spread molto OTM &mdash; conservativo</div>
                </div>
                <div>
                    <div style="font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem">POP 65&ndash;75%</div>
                    <div style="font-family:var(--font-body);font-size:0.82rem;color:var(--accent-cyan);font-weight:600">Ottimale</div>
                    <div style="font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted)">Bilanciamento rischio/rendimento</div>
                </div>
                <div>
                    <div style="font-family:var(--font-mono);font-size:0.58rem;color:var(--text-muted);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem">POP &lt; 60%</div>
                    <div style="font-family:var(--font-body);font-size:0.82rem;color:var(--accent-red);font-weight:600">Rischioso</div>
                    <div style="font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted)">Spread troppo vicino allo spot</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    _sa = _s.replace("overflow:hidden", "overflow:visible")
    st.markdown(f"<span style='font-family:var(--font-mono);font-size:0.6rem;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-secondary)'><span style='color:var(--accent-green);margin-right:0.5rem'>&#9670;</span>Analisi Spread &mdash; Bull Put Spread {fmt(bps_K_venduta,0)} / {fmt(bps_K_comprata,0)}</span>", unsafe_allow_html=True)
    a1,a2,a3,a4,a5,a6 = st.columns(6, gap="small")
    with a1:
        st.markdown(f"""<div style="{_sa}"><div style="{_e}" class="greek-tooltip">Larghezza<span class="tip-icon">?</span><div class="tip-box">Differenza in dollari tra lo strike venduto e quello comprato. Determina il rischio massimo per azione: se lo spread scade ITM perdi al massimo questa cifra meno il credito incassato.</div></div><div style="{_v};font-size:1.2rem;color:var(--accent-cyan)">${larghezza_spread}</div><div style="{_b}">tra i due strike</div></div>""", unsafe_allow_html=True)
    with a2:
        st.markdown(f"""<div style="{_sa}"><div style="{_e}" class="greek-tooltip">Break-even<span class="tip-icon">?</span><div class="tip-box">Punto esatto sotto cui inizi a perdere denaro. Calcolato come strike venduto meno il credito incassato per azione. Sopra questo livello a scadenza il trade &egrave; profittevole.</div></div><div style="{_v};font-size:1.2rem;color:var(--accent-cyan)">{fmt(bps_be,2)}</div><div style="{_b}">{fmt(be_dist,2)}% sotto spot</div></div>""", unsafe_allow_html=True)
    with a3:
        st.markdown(f"""<div style="{_sa}"><div style="{_e}" class="greek-tooltip">Distanza SD<span class="tip-icon">?</span><div class="tip-box">Quante deviazioni standard di distanza si trova lo strike venduto rispetto allo spot attuale. Sopra 1 SD = molto OTM, alta probabilit&agrave; di successo. Sotto 0.5 SD = rischioso.</div></div><div style="{_v};font-size:1.2rem;color:var(--accent-cyan)">{sd_label}</div><div style="{_b}">dal strike venduto</div></div>""", unsafe_allow_html=True)
    with a4:
        st.markdown(f"""<div style="{_sa}"><div style="{_e}" class="greek-tooltip">Take Profit 50%<span class="tip-icon">?</span><div class="tip-box">Livello consigliato per chiudere il trade in anticipo. Riacquistando lo spread a met&agrave; del credito incassato si libera il margine e si riduce il rischio residuo. &Egrave; la gestione standard tastytrade.</div></div><div style="{_v};font-size:1.2rem;color:var(--accent-green)">+{fmt(bps_tp,0)} &euro;</div><div style="{_b}">chiudi qui</div></div>""", unsafe_allow_html=True)
    with a5:
        st.markdown(f"""<div style="{_sa}"><div style="{_e}" class="greek-tooltip">Stop Loss 2x<span class="tip-icon">?</span><div class="tip-box">Livello di uscita in perdita: se il costo per chiudere lo spread raggiunge il doppio del credito incassato, esci. Limita la perdita massima gestita a 2 volte il premio ricevuto.</div></div><div style="{_v};font-size:1.2rem;color:var(--accent-red)">-{fmt(bps_sl,0)} &euro;</div><div style="{_b}">perdita max gestita</div></div>""", unsafe_allow_html=True)
    with a6:
        st.markdown(f"""<div style="{_sa}"><div style="{_e}" class="greek-tooltip">Rendimento<span class="tip-icon">?</span><div class="tip-box">Rendimento percentuale sul margine bloccato se il trade va a profitto intero. Calcolato come credito totale diviso margine totale. Non include il costo del capitale nel tempo.</div></div><div style="{_v};font-size:1.2rem;color:var(--accent-green)">{fmt(bps_rend,1)}%</div><div style="{_b}">sul margine / mese</div></div>""", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)


    # ── RIEPILOGO BPS ──
    st.markdown("<div class='section-label'>Riepilogo Operazione &mdash; Bull Put Spread</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Parametro": ["Strumento","Prezzo Attuale","Strike Venduto (STO)","Strike Comprato (BTO)",
                      "Larghezza Spread","Giorni alla Scadenza",
                      "Credito Netto per Azione","Numero Contratti",
                      "Margine per Contratto (fisso)","Margine Totale Richiesto",
                      "Credito Totale Incassato","Break-even","Take Profit (50%)",
                      "Stop Loss (2x credito)","Rendimento sul Margine"],
        "Valore":    [nome, fmt(spot,2), fmt(bps_K_venduta,2), fmt(bps_K_comprata,2),
                      f"${larghezza_spread}", f"{dte} gg",
                      f"{fmt(bps_credito,4)} ({fmt(bps_credito*100,2)} € / contratto)",
                      str(n_contratti), f"{fmt(bps_margine_c,0)} €",
                      f"{fmt(bps_margine_tot,0)} € (da avere sul conto)",
                      f"+{fmt(bps_credito_tot,0)} €",
                      fmt(bps_be,2), f"+{fmt(bps_tp,0)} €",
                      f"-{fmt(bps_sl,0)} €",
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
    Sistemi Quantitativi per il Trading di Opzioni &middot; v5.1<br>
    Dati: Yahoo Finance &nbsp;&middot;&nbsp; VIX: CBOE &nbsp;&middot;&nbsp; Motore: Black-Scholes<br>
    <span style="color:rgba(255,255,255,0.03);font-size:0.5rem">&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;</span><br>
    Solo a scopo educativo &middot; Non costituisce consulenza finanziaria
</div>
""", unsafe_allow_html=True)
