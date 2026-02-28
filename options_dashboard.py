"""
╔══════════════════════════════════════════════════════════╗
║         PHINANCE - Dashboard Vendita Put  v5.2           ║
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
# FUNZIONE DI FORMATTAZIONE ITALIANA
# ─────────────────────────────────────────────────────────
def f_val(valore, decimali=2):
    """
    Formatta i numeri con stile italiano: 
    - Punto per le migliaia
    - Virgola per i decimali
    - Sempre il numero di decimali richiesto (es. 50,00 o 0,50)
    """
    if valore is None: return "N/D"
    # Formatta con virgola per migliaia e punto per decimali, poi scambia
    s = f"{valore:,.{decimali}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# ─────────────────────────────────────────────────────────
# CSS — LUXURY FINTECH v4.1
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@300;400;500&display=swap');

:root {
  --bg-base:         #060A0E;
  --bg-surface:      #0A1118;
  --bg-elevated:     #0F1822;
  --bg-card:         #0C1520;
  --border-subtle:   rgba(255,255,255,0.055);
  --border-medium:   rgba(255,255,255,0.09);
  --text-primary:    #EEF4FF;
  --text-secondary:  #7A90B0;
  --text-muted:      #3E526A;
  --accent-cyan:     #00C2FF;
  --accent-green:    #00E5A0;
  --accent-gold:     #FFB547;
  --accent-red:      #FF5A5A;
  --radius-md:       12px;
  --radius-lg:       18px;
  --radius-xl:       24px;
  --font-body:       'DM Sans', sans-serif;
  --font-mono:       'DM Mono', monospace;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-base) !important;
    color: var(--text-primary);
    font-family: var(--font-body);
}
.block-container { padding: 2.5rem 3rem !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1118 0%, #080E15 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

/* ── HEADER ── */
.ph-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 2.2rem 0 1.8rem 0; border-bottom: 1px solid var(--border-subtle); margin-bottom: 2rem;
}
.ph-logo {
    font-size: 2.4rem; font-weight: 700; letter-spacing: -0.04em;
    background: linear-gradient(120deg, #FFFFFF 0%, #80DDFF 40%, var(--accent-cyan) 70%, #0077BB 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* ── SIGNAL BANNER ── */
.signal-banner {
    display: flex; align-items: center; gap: 1.2rem; border-radius: var(--radius-md);
    padding: 1rem 1.6rem; margin-bottom: 2rem; border: 1px solid;
}
.signal-banner.verde  { background: rgba(0,229,160,0.04);  border-color: rgba(0,229,160,0.18); }
.signal-banner.giallo { background: rgba(255,181,71,0.04);  border-color: rgba(255,181,71,0.18); }
.signal-banner.rosso  { background: rgba(255,90,90,0.04);   border-color: rgba(255,90,90,0.18); }

/* ── KPI CARDS ── */
.kpi-card {
    background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl);
    padding: 1.6rem; display: flex; flex-direction: column; justify-content: space-between; min-height: 180px;
}
.kpi-eyebrow { font-family: var(--font-mono); font-size: 0.58rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.14em; }
.kpi-value { font-size: 2.4rem; font-weight: 700; color: var(--text-primary); margin-top: 0.5rem; }
.kpi-value.cyan  { color: var(--accent-cyan); }
.kpi-value.green { color: var(--accent-green); }
.kpi-value.gold  { color: var(--accent-gold); }
.kpi-value.red   { color: var(--accent-red); }

/* ── PANELS ── */
.panel {
    background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); padding: 1.8rem 2rem;
}
.panel-title { font-family: var(--font-mono); font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.8rem; margin-bottom: 1.2rem; }
.panel-key { font-family: var(--font-mono); font-size: 0.68rem; color: var(--text-muted); }
.panel-val { font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-secondary); }
.panel-val.cyan  { color: var(--accent-cyan); }
.panel-val.green { color: var(--accent-green); }
.panel-val.red   { color: var(--accent-red); }
.panel-val.big   { font-size: 1.3rem; font-weight: 700; }

/* ── CRISIS PANEL ── */
.crisis-panel {
    background: linear-gradient(135deg, rgba(255,90,90,0.04) 0%, rgba(10,17,24,0.95) 100%);
    border: 1px solid rgba(255,90,90,0.14); border-radius: var(--radius-xl); padding: 1.8rem 2rem;
}
.crisis-header { font-family: var(--font-mono); font-size: 0.6rem; color: rgba(255,90,90,0.5); text-transform: uppercase; margin-bottom: 1rem; }
.crisis-key { font-family: var(--font-mono); font-size: 0.68rem; color: rgba(255,90,90,0.4); }
.crisis-val { font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-secondary); }

/* ── DELTA COLORS ── */
.ph-delta-green [data-testid="stMetricDelta"] { color: var(--accent-green) !important; }
.ph-delta-gold  [data-testid="stMetricDelta"] { color: var(--accent-gold)  !important; }
.ph-delta-red   [data-testid="stMetricDelta"] { color: var(--accent-red)   !important; }
.ph-delta-green svg, .ph-delta-gold svg, .ph-delta-red svg { display: none !important; }

.live-bar-wrap [data-testid="stMetricValue"] { color: var(--accent-cyan) !important; font-size: 1.8rem !important; }

.section-label { font-family: var(--font-mono); font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase; margin: 2rem 0 1rem 0; display: flex; align-items: center; gap: 1rem; }
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--border-subtle); }

.ph-footer { text-align: center; padding: 2.5rem 0; border-top: 1px solid var(--border-subtle); margin-top: 3rem; font-family: var(--font-mono); font-size: 0.6rem; color: var(--text-muted); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# LOGICA DATI & CALCOLI
# ═══════════════════════════════════════════════════════════

TICKER_DISPONIBILI = {
    "S&P 500 (SPY)":                 "SPY",
    "S&P 500 Indice (^GSPC)":        "^GSPC",
    "NASDAQ 100 (QQQ)":              "QQQ",
    "Dow Jones (^DJI)":              "^DJI",
    "Apple (AAPL)":                  "AAPL",
    "Tesla (TSLA)":                  "TSLA",
    "Nvidia (NVDA)":                 "NVDA",
    "Altro (inserisci manualmente)": "MANUALE",
}

@st.cache_data(ttl=300)
def recupera_dati_mercato(ticker: str) -> dict:
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        s = yf.Ticker(ticker)
        h = s.history(period="1y")
        if h.empty: return {"errore": "Dati non trovati"}
        
        spot = float(h["Close"].iloc[-1])
        var  = ((spot - h["Close"].iloc[-2]) / h["Close"].iloc[-2] * 100) if len(h) >= 2 else 0.0
        ret  = np.log(h["Close"] / h["Close"].shift(1)).dropna()
        vol_st = float(ret.tail(30).std() * np.sqrt(252) * 100)
        
        # IV Rank
        vol_rolling = ret.rolling(30).std() * np.sqrt(252) * 100
        vol_rolling = vol_rolling.dropna()
        v_min, v_max, v_now = vol_rolling.min(), vol_rolling.max(), vol_rolling.iloc[-1]
        iv_rank = ((v_now - v_min) / (v_max - v_min) * 100) if v_max > v_min else 50.0

        # VIX
        vix_h = yf.Ticker("^VIX").history(period="5d")
        vix_val = round(float(vix_h["Close"].iloc[-1]), 2) if not vix_h.empty else None

        return {
            "prezzo_spot": spot, "variazione_gg": var, "vol_storica": vol_st,
            "iv_rank": iv_rank, "vix": vix_val, "nome": s.info.get("longName", ticker),
            "ts_spot": ts, "ts_vol": ts, "ts_vix": ts, "ts_ivrank": ts, "errore": None
        }
    except Exception as e: return {"errore": str(e)}

# ── MOTORE BLACK-SCHOLES ──
@dataclass
class Par: S: float; K: float; T: float; r: float; sigma: float

def d1d2(p: Par):
    if p.T <= 0 or p.sigma <= 0: return 0.0, 0.0
    d1 = (np.log(p.S/p.K) + (p.r + 0.5*p.sigma**2)*p.T) / (p.sigma*np.sqrt(p.T))
    return d1, d1 - p.sigma*np.sqrt(p.T)

def prezzo_put(p: Par):
    d1, d2 = d1d2(p); return max(p.K*np.exp(-p.r*p.T)*si.norm.cdf(-d2) - p.S*si.norm.cdf(-d1), 0.0)

def calc_greche(p: Par):
    if p.T <= 0: return {"delta":0,"theta":0,"gamma":0,"vega":0,"rho":0}
    d1, d2 = d1d2(p); f = si.norm.pdf(d1)
    return {
        "delta": -si.norm.cdf(-d1),
        "theta": (-(p.S*f*p.sigma)/(2*np.sqrt(p.T)) + p.r*p.K*np.exp(-p.r*p.T)*si.norm.cdf(-d2))/365,
        "gamma": f/(p.S*p.sigma*np.sqrt(p.T)),
        "vega":  p.S*f*np.sqrt(p.T)/100,
        "rho":   -p.K*p.T*np.exp(-p.r*p.T)*si.norm.cdf(-d2)/100
    }

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### STRUMENTO")
    scelta = st.selectbox("Sottostante", options=list(TICKER_DISPONIBILI.keys()), index=0)
    tk = TICKER_DISPONIBILI[scelta]
    if tk == "MANUALE": tk = st.text_input("Ticker Yahoo", value="SPY").upper()
    aggiorna = st.button("↻ AGGIORNA DATI")

    st.markdown("---")
    dte = st.slider("DTE (Giorni)", 1, 365, 45)
    iv_pct = st.slider("IV (%)", 1.0, 150.0, 20.0, 0.5)
    r_pct = st.number_input("Risk-Free %", 0.0, 10.0, 4.2, 0.1)
    
    st.markdown("---")
    n_contratti = st.slider("N. Contratti", 1, 50, 1)
    marg_pct = st.slider("Margine Broker %", 5, 50, 15)
    crash = st.slider("Scenario Crisi %", 5, 50, 20)
    prob_t = st.slider("Prob. Obiettivo %", 70, 99, 84)

# ═══════════════════════════════════════════════════════════
# ELABORAZIONE
# ═══════════════════════════════════════════════════════════
if "dati" not in st.session_state or aggiorna:
    st.session_state.dati = recupera_dati_mercato(tk)
    if st.session_state.dati["vix"] and aggiorna: iv_pct = st.session_state.dati["vix"]

d = st.session_state.dati
if d["errore"]: st.error(d["errore"]); st.stop()

# Calcoli base
S, T, sigma, r = d["prezzo_spot"], dte/365, iv_pct/100, r_pct/100
K = round(S*np.exp((r-0.5*sigma**2)*T + sigma*np.sqrt(T)*si.norm.ppf(1.0-prob_t/100)), 2)
p = Par(S, K, T, r, sigma)
prem = prezzo_put(p)
gre = calc_greche(p)
prob = si.norm.cdf(d1d2(p)[1])

# Calcoli monetari
mult = 100
mc = K * mult * (marg_pct/100)
marg_tot = n_contratti * mc
ptot = prem * n_contratti * mult
thday = abs(gre["theta"]) * n_contratti * mult
rend = (ptot / marg_tot * 100) if marg_tot > 0 else 0
dist = (S - K) / S * 100

# Crisi
Sc = S * (1 - crash/100)
lc = (max(K - Sc, 0) - prem) * n_contratti * mult

# ═══════════════════════════════════════════════════════════
# INTERFACCIA UTENTE
# ═══════════════════════════════════════════════════════════

st.markdown(f"""
<div class="ph-header">
    <span class="ph-logo">Phinance</span>
    <div style="text-align:right">
        <div style="font-family:var(--font-mono); font-size:0.7rem; color:var(--accent-cyan)">DASHBOARD V5.2</div>
        <div style="font-size:0.6rem; color:var(--text-muted)">SOLO SCOPO EDUCATIVO</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LIVE BAR ──
# Logica Frecce: ▲ (Green), ↔ (Gold), ▼ (Red)
if d["variazione_gg"] > 0.05:   s_arr, s_cl = f"▲ +{f_val(d['variazione_gg'])}%", "green"
elif d["variazione_gg"] < -0.05: s_arr, s_cl = f"▼ {f_val(d['variazione_gg'])}%", "red"
else:                           s_arr, s_cl = f"↔ {f_val(d['variazione_gg'])}%", "gold"

if d["vol_storica"] >= 25:      v_arr, v_cl = "▲ Alta", "green"
elif d["vol_storica"] < 15:     v_arr, v_cl = "▼ Bassa", "red"
else:                           v_arr, v_cl = "↔ Media", "gold"

if d["iv_rank"] >= 60:          i_arr, i_cl = "▲ Alto", "green"
elif d["iv_rank"] < 35:         i_arr, i_cl = "▼ Basso", "red"
else:                           i_arr, i_cl = "↔ Medio", "gold"

vix_v = d["vix"]
if vix_v and vix_v >= 20:       vx_arr, vx_cl = "▲ Elevato", "green"
elif vix_v and vix_v < 15:      vx_arr, vx_cl = "▼ Basso", "red"
else:                           vx_arr, vx_cl = "↔ Normale", "gold"

st.markdown("<div class='live-bar-wrap'>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns(4)
with b1: st.markdown(f"<div class='ph-delta-{s_cl}'>", unsafe_allow_html=True); st.metric("● PREZZO SPOT", f_val(S), s_arr, delta_color="off")
with b2: st.markdown(f"<div class='ph-delta-{v_cl}'>", unsafe_allow_html=True); st.metric("● VOL. STORICA", f"{f_val(d['vol_storica'])}%", v_arr, delta_color="off")
with b3: st.markdown(f"<div class='ph-delta-{i_cl}'>", unsafe_allow_html=True); st.metric("● IV RANK", f"{f_val(d['iv_rank'], 0)}/100", i_arr, delta_color="off")
with b4: st.markdown(f"<div class='ph-delta-{vx_cl}'>", unsafe_allow_html=True); st.metric("● VIX INDEX", f_val(vix_v) if vix_v else "N/D", vx_arr, delta_color="off")
st.markdown("</div>", unsafe_allow_html=True)

# ── POSIZIONE ──
st.markdown(f"""
<div class="panel" style="margin-top:2rem; margin-bottom:1.5rem">
    <div class="panel-title">DETTAGLIO POSIZIONE</div>
    <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:20px">
        <div><div class="panel-key">Contratti</div><div class="panel-val big cyan">{n_contratti}</div></div>
        <div><div class="panel-key">Margine Totale</div><div class="panel-val big gold">{f_val(marg_tot)} €</div></div>
        <div><div class="panel-key">Incasso Premi</div><div class="panel-val big green">+{f_val(ptot)} €</div></div>
        <div><div class="panel-key">Theta / Giorno</div><div class="panel-val big green">+{f_val(thday)} €</div></div>
        <div><div class="panel-key">ROI Mensile</div><div class="panel-val big green">{f_val(rend)}%</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ──
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-eyebrow">Strike Target</div><div class="kpi-value cyan">{f_val(K)}</div><div class="kpi-key">{f_val(dist)}% sotto lo spot</div></div>', unsafe_allow_html=True)
with c2: 
    cl_p = "green" if prob >= 0.85 else "gold" if prob >= 0.75 else "red"
    st.markdown(f'<div class="kpi-card"><div class="kpi-eyebrow">Prob. Successo</div><div class="kpi-value {cl_p}">{f_val(prob*100)}%</div><div class="kpi-key">Probabilità OTM</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-eyebrow">Premio Unitario</div><div class="kpi-value green">{f_val(prem)}</div><div class="kpi-key">{f_val(prem*100)} € a contratto</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-eyebrow">Pareggio</div><div class="kpi-value">{f_val(K-prem)}</div><div class="kpi-key">Break-even price</div></div>', unsafe_allow_html=True)

# ── GRECHE ──
st.markdown(f"""
<div class="panel" style="margin-top:1.5rem">
    <div class="panel-title">GRECHE DELLA POSIZIONE</div>
    <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:10px">
        <div><div class="panel-key">Delta</div><div class="panel-val cyan">{f_val(gre['delta'], 4)}</div></div>
        <div><div class="panel-key">Theta</div><div class="panel-val green">+{f_val(gre['theta'], 4)}</div></div>
        <div><div class="panel-key">Gamma</div><div class="panel-val">{f_val(gre['gamma'], 6)}</div></div>
        <div><div class="panel-key">Vega</div><div class="panel-val">{f_val(gre['vega'], 4)}</div></div>
        <div><div class="panel-key">Rho</div><div class="panel-val">{f_val(gre['rho'], 4)}</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CRISI ──
st.markdown(f"""
<div class="crisis-panel" style="margin-top:1.5rem">
    <div class="crisis-header">SCENARIO DI CRISI (CROLLO {crash}%)</div>
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:10px">
        <div><div class="crisis-key">Prezzo Post-Crollo</div><div class="crisis-val">{f_val(Sc)}</div></div>
        <div><div class="crisis-key">Perdita Netta</div><div class="crisis-val red" style="font-weight:700">{f_val(lc)} €</div></div>
        <div><div class="crisis-key">Impatto su Margine</div><div class="crisis-val red">{f_val(lc/marg_tot*100 if marg_tot>0 else 0)}%</div></div>
        <div><div class="crisis-key">Stato</div><div class="crisis-val">{"⚠️ ASSEGNAZIONE" if Sc < K else "✅ OTM"}</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── RIEPILOGO ──
st.markdown("<div class='section-label'>Riepilogo Tabellare</div>", unsafe_allow_html=True)
df_data = {
    "Parametro": ["Strumento", "Prezzo Spot", "Strike", "Distanza Strike", "Premio Unitario", "Incasso Totale", "Margine Totale", "ROI Mensile", "Probabilità"],
    "Valore": [
        d["nome"], f"{f_val(S)} €", f"{f_val(K)} €", f"{f_val(dist)}%", f"{f_val(prem)} €", 
        f"{f_val(ptot)} €", f"{f_val(marg_tot)} €", f"{f_val(rend)}%", f"{f_val(prob*100)}%"
    ]
}
st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

st.markdown(f"""
<div class="ph-footer">
    Phinance Dashboard v5.2 | {d['ts_spot']} | Dati Yahoo Finance<br>
    Questo software ha scopo puramente informativo. Il trading comporta rischi elevati.
</div>
""", unsafe_allow_html=True)
