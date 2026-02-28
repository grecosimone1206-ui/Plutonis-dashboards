"""
╔══════════════════════════════════════════════════════════╗
║         PHINANCE - Dashboard Vendita Put  v5.5           ║
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
    """Formatta i numeri: punto per migliaia e virgola per decimali (es. 1.250,50)"""
    if valore is None or (isinstance(valore, str) and valore == "N/D"):
        return "N/D"
    try:
        v = float(valore)
        s = f"{v:,.{decimali}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valore)

# ─────────────────────────────────────────────────────────
# CSS — LUXURY FINTECH v4.5
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
  --accent-green-dim:rgba(0,229,160,0.08);
  --accent-gold:     #FFB547;
  --accent-gold-dim: rgba(255,181,71,0.08);
  --accent-red:      #FF5A5A;
  --accent-red-dim:  rgba(255,90,90,0.06);
  --radius-md:       12px;
  --radius-xl:       24px;
  --font-body:       'DM Sans', sans-serif;
  --font-mono:       'DM Mono', monospace;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-base) !important;
    color: var(--text-primary);
    font-family: var(--font-body);
}

/* ── SIDEBAR STYLE ── */
[data-testid="stSidebar"] { background: var(--bg-surface) !important; border-right: 1px solid var(--border-subtle) !important; }
[data-testid="stSidebar"] label { font-family: var(--font-mono) !important; font-size: 0.65rem !important; color: var(--text-muted) !important; text-transform: uppercase !important; }

/* ── SIGNAL BANNER ── */
.signal-banner { display: flex; align-items: center; gap: 1.2rem; border-radius: var(--radius-md); padding: 1rem 1.6rem; margin-bottom: 2rem; border: 1px solid; }
.signal-banner.verde  { background: rgba(0,229,160,0.04);  border-color: rgba(0,229,160,0.18); }
.signal-banner.giallo { background: rgba(255,181,71,0.04);  border-color: rgba(255,181,71,0.18); }
.signal-banner.rosso  { background: rgba(255,90,90,0.04);   border-color: rgba(255,90,90,0.18); }
.signal-dot { width: 8px; height: 8px; border-radius: 50%; }
.signal-dot.verde  { background: var(--accent-green); box-shadow: 0 0 10px var(--accent-green); }
.signal-dot.giallo { background: var(--accent-gold); }
.signal-dot.rosso  { background: var(--accent-red); }
.signal-label { font-family: var(--font-mono); font-size: 0.68rem; font-weight: 500; text-transform: uppercase; }
.signal-banner.verde  .signal-label { color: var(--accent-green); }
.signal-banner.giallo .signal-label { color: var(--accent-gold); }
.signal-banner.rosso  .signal-label { color: var(--accent-red); }

/* ── KPI & PANELS ── */
.kpi-card { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); padding: 1.6rem; height: 100%; min-height: 180px; transition: transform 0.3s; }
.kpi-card:hover { transform: translateY(-3px); border-color: rgba(0,194,255,0.2); }
.kpi-value { font-size: 2.6rem; font-weight: 700; line-height: 1; margin-bottom: 0.5rem; }
.kpi-value.cyan { color: var(--accent-cyan); }
.kpi-value.green { color: var(--accent-green); }
.kpi-value.gold { color: var(--accent-gold); }
.kpi-value.red { color: var(--accent-red); }
.panel { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); padding: 1.8rem 2rem; }
.panel-val.big { font-size: 1.3rem; font-weight: 700; font-family: var(--font-mono); }

/* ── DELTA COLORI & HIDE SVG ── */
.ph-delta-green [data-testid="stMetricDelta"] { color: var(--accent-green) !important; }
.ph-delta-gold  [data-testid="stMetricDelta"] { color: var(--accent-gold)  !important; }
.ph-delta-red   [data-testid="stMetricDelta"] { color: var(--accent-red)   !important; }
[data-testid="stMetricDelta"] svg { display: none !important; }

/* ── ALTRI STILI ── */
.ph-header { display: flex; align-items: center; justify-content: space-between; padding: 2.2rem 0; border-bottom: 1px solid var(--border-subtle); margin-bottom: 2rem; }
.ph-logo { font-size: 2.4rem; font-weight: 700; background: linear-gradient(120deg, #FFFFFF, var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.crisis-panel { background: linear-gradient(135deg, rgba(255,90,90,0.04), #0A1118); border: 1px solid rgba(255,90,90,0.14); border-radius: var(--radius-xl); padding: 1.8rem 2rem; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# LOGICA DATI
# ═══════════════════════════════════════════════════════════

TICKER_DISPONIBILI = {
    "S&P 500 (SPY)": "SPY", "S&P 500 Indice (^GSPC)": "^GSPC",
    "NASDAQ 100 (QQQ)": "QQQ", "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA", "Altro": "MANUALE"
}

@st.cache_data(ttl=300)
def recupera_dati(ticker):
    try:
        s = yf.Ticker(ticker); h = s.history(period="1y")
        if h.empty: return None
        spot = h["Close"].iloc[-1]
        var = ((spot - h["Close"].iloc[-2]) / h["Close"].iloc[-2] * 100)
        ret = np.log(h["Close"] / h["Close"].shift(1)).dropna()
        vol_st = float(ret.tail(30).std() * np.sqrt(252) * 100)
        v_roll = ret.rolling(30).std() * np.sqrt(252) * 100
        iv_rank = ((vol_st - v_roll.min()) / (v_roll.max() - v_roll.min()) * 100)
        vix_h = yf.Ticker("^VIX").history(period="5d")
        vix_val = vix_h["Close"].iloc[-1] if not vix_h.empty else 20.0
        return {"spot": spot, "var": var, "vol": vol_st, "ivr": iv_rank, "vix": vix_val, "nome": ticker, "ts": datetime.now().strftime("%H:%M:%S")}
    except: return None

# ═══════════════════════════════════════════════════════════
# MOTORE CALCOLO
# ═══════════════════════════════════════════════════════════

def get_bs_metrics(S, K, T_days, r_pct, sigma_pct):
    T, r, sigma = T_days/365, r_pct/100, sigma_pct/100
    if T <= 0: return 0.0, 0.0, {}
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    prezzo = max(K*np.exp(-r*T)*si.norm.cdf(-d2) - S*si.norm.cdf(-d1), 0.0)
    prob = si.norm.cdf(d2)
    greche = {
        "delta": -si.norm.cdf(-d1),
        "gamma": si.norm.pdf(d1)/(S*sigma*np.sqrt(T)),
        "theta": (-(S*si.norm.pdf(d1)*sigma)/(2*np.sqrt(T)) + r*K*np.exp(-r*T)*si.norm.cdf(-d2))/365,
        "vega": S*si.norm.pdf(d1)*np.sqrt(T)/100
    }
    return prezzo, prob, greche

# ═══════════════════════════════════════════════════════════
# SIDEBAR (MANTENUTA ORIGINALE)
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("<h3 style='font-family:DM Mono; font-size:0.8rem; color:#7A90B0;'>CONFIGURAZIONE</h3>", unsafe_allow_html=True)
    scelta = st.selectbox("Sottostante", options=list(TICKER_DISPONIBILI.keys()), index=0)
    tk = TICKER_DISPONIBILI[scelta]
    if tk == "MANUALE": tk = st.text_input("Ticker Yahoo", "SPY").upper()
    
    st.divider()
    dte = st.slider("DTE (Giorni alla scadenza)", 1, 90, 45)
    iv_manuale = st.slider("IV stimata (%)", 5.0, 100.0, 20.0)
    r_pct = st.number_input("Tasso Risk-Free (%)", 0.0, 10.0, 4.0)
    
    st.divider()
    n_contratti = st.number_input("N. Contratti", 1, 100, 3)
    marg_pct = st.slider("Margine Broker (%)", 5, 40, 15)
    crash_pct = st.slider("Scenario Crisi (%)", 5, 40, 20)
    prob_t = st.slider("Probabilità Target (%)", 70, 95, 84)

# ═══════════════════════════════════════════════════════════
# CALCOLI FINALI
# ═══════════════════════════════════════════════════════════

d = recupera_dati(tk)
if not d: st.error("Errore recupero dati"); st.stop()

# Strike target per probabilità scelta
sigma_calc = iv_manuale/100
K_target = d["spot"] * np.exp((r_pct/100 - 0.5 * sigma_calc**2) * (dte/365) + sigma_calc * np.sqrt(dte/365) * si.norm.ppf(1 - prob_t/100))
K_target = round(K_target, 2)

prezzo, prob, greche = get_bs_metrics(d["spot"], K_target, dte, r_pct, iv_manuale)

# Monetari
mult = 100
marg_singolo = K_target * mult * (marg_pct/100)
marg_totale = marg_singolo * n_contratti
incasso_totale = prezzo * mult * n_contratti
roi_mese = (incasso_totale / marg_totale * 100) if marg_totale > 0 else 0

# ═══════════════════════════════════════════════════════════
# RENDER INTERFACCIA
# ═══════════════════════════════════════════════════════════

# HEADER
st.markdown(f"""
<div class="ph-header">
    <div style="display:flex;align-items:center;gap:1.2rem">
        <span class="ph-logo">Phinance</span>
        <div style="width:1px;height:2rem;background:var(--border-medium)"></div>
        <span style="font-family:var(--font-mono);font-size:0.68rem;color:var(--text-muted);letter-spacing:0.14em;text-transform:uppercase">Dashboard Put · Black-Scholes Engine</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 1. BARRA DATI LIVE (CON FRECCE E FORMATO ITA)
# Spot
if d["var"] > 0.05:   s_arr, s_cl = f"▲ +{f_val(d['var'])}%", "green"
elif d["var"] < -0.05: s_arr, s_cl = f"▼ {f_val(d['var'])}%", "red"
else:                 s_arr, s_cl = f"↔ {f_val(d['var'])}%", "gold"

# Volatilità
if d["vol"] >= 25:     v_arr, v_cl = "▲ Alta", "green"
elif d["vol"] < 15:    v_arr, v_cl = "▼ Bassa", "red"
else:                  v_arr, v_cl = "↔ Media", "gold"

# IV Rank
if d["ivr"] >= 60:     i_arr, i_cl = "▲ Alto", "green"
elif d["ivr"] < 35:    i_arr, i_cl = "▼ Basso", "red"
else:                  i_arr, i_cl = "↔ Medio", "gold"

# VIX
if d["vix"] >= 20:     vx_arr, vx_cl = "▲ Elevato", "green"
elif d["vix"] < 15:    vx_arr, vx_cl = "▼ Basso", "red"
else:                  vx_arr, vx_cl = "↔ Normale", "gold"

st.markdown("<div class='live-bar-wrap'>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns(4)
with b1: st.markdown(f"<div class='ph-delta-{s_cl}'>", unsafe_allow_html=True); st.metric("SPOT", f_val(d['spot']), s_arr, delta_color="off")
with b2: st.markdown(f"<div class='ph-delta-{v_cl}'>", unsafe_allow_html=True); st.metric("VOL. STORICA", f"{f_val(d['vol'])}%", v_arr, delta_color="off")
with b3: st.markdown(f"<div class='ph-delta-{i_cl}'>", unsafe_allow_html=True); st.metric("IV RANK", f"{f_val(d['ivr'],0)}/100", i_arr, delta_color="off")
with b4: st.markdown(f"<div class='ph-delta-{vx_cl}'>", unsafe_allow_html=True); st.metric("VIX", f_val(d['vix']), vx_arr, delta_color="off")
st.markdown("</div>", unsafe_allow_html=True)

# 2. IL SEMAFORO (CONDIZIONI)
score = 0
if d["vix"] > 20: score += 40
if d["ivr"] > 50: score += 30
if d["vol"] > 20: score += 30

if score >= 70:    cl, txt, dsc = "verde", "Condizioni Ottime", "Premi gonfiati, volatilità alta: momento ideale per vendere."
elif score >= 40:  cl, txt, dsc = "giallo", "Condizioni Neutre", "Mercato in equilibrio, valutare bene il rapporto rischio/rendimento."
else:             cl, txt, dsc = "rosso", "Condizioni Sfavorevoli", "Premi bassi e volatilità compressa: rischio asimmetrico."

st.markdown(f"""
<div class="signal-banner {cl}">
    <span class="signal-dot {cl}"></span>
    <span class="signal-label">{txt}</span>
    <span class="signal-text">{dsc} (Punteggio: {score}/100)</span>
</div>
""", unsafe_allow_html=True)

# 3. DETTAGLIO POSIZIONE
st.markdown(f"""
<div class="panel" style="margin-bottom:1.5rem">
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0">
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div style="color:var(--text-muted);font-size:0.6rem;text-transform:uppercase;margin-bottom:0.4rem">Contratti</div>
            <div class="panel-val big cyan">{n_contratti}</div>
        </div>
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div style="color:var(--text-muted);font-size:0.6rem;text-transform:uppercase;margin-bottom:0.4rem">Margine Totale</div>
            <div class="panel-val big gold">{f_val(marg_totale, 0)} €</div>
        </div>
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div style="color:var(--text-muted);font-size:0.6rem;text-transform:uppercase;margin-bottom:0.4rem">Incasso Premi</div>
            <div class="panel-val big green">+{f_val(incasso_totale, 0)} €</div>
        </div>
        <div style="padding:0.6rem 1.2rem;border-right:1px solid rgba(255,255,255,0.04)">
            <div style="color:var(--text-muted);font-size:0.6rem;text-transform:uppercase;margin-bottom:0.4rem">Theta Tot/GG</div>
            <div class="panel-val big green">+{f_val(abs(greche['theta']*n_contratti*mult))} €</div>
        </div>
        <div style="padding:0.6rem 1.2rem">
            <div style="color:var(--text-muted);font-size:0.6rem;text-transform:uppercase;margin-bottom:0.4rem">ROI Mese</div>
            <div class="panel-val big green">{f_val(roi_mese)}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. KPI CARDS
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f"<div class='kpi-card'><div style='color:var(--text-muted);font-size:0.6rem;margin-bottom:0.8rem'>🎯 STRIKE TARGET</div><div class='kpi-value cyan'>{f_val(K_target)}</div><div style='color:var(--text-muted);font-size:0.7rem'>{f_val((d['spot']-K_target)/d['spot']*100)}% sotto lo spot</div></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='kpi-card'><div style='color:var(--text-muted);font-size:0.6rem;margin-bottom:0.8rem'>✦ PROBABILITÀ OK</div><div class='kpi-value green'>{f_val(prob*100)}%</div><div style='color:var(--text-muted);font-size:0.7rem'>Successo a scadenza</div></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='kpi-card'><div style='color:var(--text-muted);font-size:0.6rem;margin-bottom:0.8rem'>◈ PREMIO UNITARIO</div><div class='kpi-value green'>{f_val(prezzo)}</div><div style='color:var(--text-muted);font-size:0.7rem'>{f_val(prezzo*100)} € per contratto</div></div>", unsafe_allow_html=True)
with c4: st.markdown(f"<div class='kpi-card'><div style='color:var(--text-muted);font-size:0.6rem;margin-bottom:0.8rem'>◎ MARGINE UNITARIO</div><div class='kpi-value gold'>{f_val(marg_singolo,0)} €</div><div style='color:var(--text-muted);font-size:0.7rem'>{marg_pct}% del nozionale</div></div>", unsafe_allow_html=True)

# 5. GRECHE & CRISI
st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
g1, g2 = st.columns([2, 1])
with g1:
    st.markdown(f"""
    <div class="panel">
        <div style="font-family:var(--font-mono);font-size:0.6rem;color:var(--text-muted);margin-bottom:1rem;border-bottom:1px solid var(--border-subtle);padding-bottom:0.5rem">∑ LETTERE GRECHE (PORTAFOGLIO)</div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:15px">
            <div><div style="color:var(--text-muted);font-size:0.65rem">Delta Tot.</div><div class="cyan" style="font-family:var(--font-mono)">{f_val(greche['delta']*n_contratti*mult,1)}</div></div>
            <div><div style="color:var(--text-muted);font-size:0.65rem">Gamma Tot.</div><div style="font-family:var(--font-mono)">{f_val(greche['gamma']*n_contratti*mult,4)}</div></div>
            <div><div style="color:var(--text-muted);font-size:0.65rem">Theta Tot.</div><div class="green" style="font-family:var(--font-mono)">+{f_val(greche['theta']*n_contratti*mult)} €</div></div>
            <div><div style="color:var(--text-muted);font-size:0.65rem">Vega Tot.</div><div style="font-family:var(--font-mono)">{f_val(greche['vega']*n_contratti*mult)} €</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with g2:
    p_crash = d["spot"] * (1 - crash_pct/100)
    loss = max(K_target - p_crash, 0) - prezzo
    loss_tot = loss * n_contratti * mult
    st.markdown(f"""
    <div class="crisis-panel">
        <div style="font-family:var(--font-mono);font-size:0.6rem;color:var(--accent-red);margin-bottom:1rem">⚠ CRISI -{crash_pct}%</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem"><span style="color:var(--text-muted);font-size:0.7rem">Prezzo:</span><span style="font-family:var(--font-mono)">{f_val(p_crash)}</span></div>
        <div style="display:flex;justify-content:space-between"><span style="color:var(--text-muted);font-size:0.7rem">P&L Netto:</span><span style="font-family:var(--font-mono);color:var(--accent-red);font-weight:700">{f_val(loss_tot,0)} €</span></div>
    </div>
    """, unsafe_allow_html=True)

# 6. RIEPILOGO TABELLARE
st.markdown("<div style='margin-top:2.5rem'></div>", unsafe_allow_html=True)
df_res = pd.DataFrame({
    "Parametro": ["Strumento", "Prezzo Spot", "Strike Scelto", "Distanza", "Prob. Successo", "Margine Totale", "Incasso Premi", "Punto Pareggio", "ROI Operazione"],
    "Valore": [
        tk, f"{f_val(d['spot'])} €", f"{f_val(K_target)} €", f"{f_val((d['spot']-K_target)/d['spot']*100)}%",
        f"{f_val(prob*100)}%", f"{f_val(marg_totale,0)} €", f"{f_val(incasso_totale,0)} €",
        f"{f_val(K_target-prezzo)} €", f"{f_val(roi_mese)}% / mese"
    ]
})
st.table(df_res)

# FOOTER
st.markdown("<div style='text-align:center; padding:2rem; font-family:var(--font-mono); font-size:0.6rem; color:var(--text-muted);'>Phinance v5.5 · Solo a scopo educativo · Dati Yahoo Finance</div>", unsafe_allow_html=True)
