"""
╔══════════════════════════════════════════════════════════╗
║         PLUTONIS - Quant Options Dashboard               ║
║         Motore Quantitativo per Short Put Seller         ║
╚══════════════════════════════════════════════════════════╝

Librerie richieste:
    pip install streamlit numpy pandas scipy plotly

Avvio:
    streamlit run options_dashboard.py
"""

import numpy as np
import pandas as pd
import scipy.stats as si
import streamlit as st
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import Optional

# ─────────────────────────────────────────────────────────
# CONFIGURAZIONE PAGINA
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plutonis | Quant Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# CSS PERSONALIZZATO  (stile "terminal quant")
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;500;700&display=swap');

/* Sfondo globale */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #050A0F;
    color: #C8D8E8;
    font-family: 'Rajdhani', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07111B 0%, #050A0F 100%);
    border-right: 1px solid #0D2137;
}
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stSelectbox label {
    color: #5EAAD7 !important;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Header titolo */
h1 { font-family: 'Rajdhani', sans-serif; font-weight: 700; color: #E8F4FF; letter-spacing: 0.05em; }
h2 { font-family: 'Rajdhani', sans-serif; color: #5EAAD7; border-bottom: 1px solid #0D2137; padding-bottom: 4px; }
h3 { font-family: 'Share Tech Mono', monospace; color: #7EC8E3; font-size: 0.85rem; letter-spacing: 0.12em; }

/* Card metrica personalizzata */
.metric-card {
    background: linear-gradient(135deg, #071828 0%, #0D2137 100%);
    border: 1px solid #1A3A55;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00C4FF, #0066CC);
}
.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #4A7A9B;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #00D4FF;
    line-height: 1;
}
.metric-delta {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #2ECC71;
    margin-top: 4px;
}
.metric-delta.danger { color: #E74C3C; }
.metric-delta.warning { color: #F39C12; }

/* Semaforo IV */
.semaforo {
    display: inline-block;
    width: 14px; height: 14px;
    border-radius: 50%;
    margin-right: 8px;
    vertical-align: middle;
}
.semaforo.green  { background: #2ECC71; box-shadow: 0 0 10px #2ECC71; }
.semaforo.yellow { background: #F39C12; box-shadow: 0 0 10px #F39C12; }
.semaforo.red    { background: #E74C3C; box-shadow: 0 0 10px #E74C3C; }

/* Box alert scenario peggiore */
.worst-case-box {
    background: linear-gradient(135deg, #1A0A0A, #2A1010);
    border: 1px solid #5C1A1A;
    border-left: 4px solid #E74C3C;
    border-radius: 6px;
    padding: 16px 20px;
}
.greche-box {
    background: #071828;
    border: 1px solid #0D2137;
    border-radius: 6px;
    padding: 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.82rem;
    line-height: 2;
}
.grecа-row { display: flex; justify-content: space-between; border-bottom: 1px solid #0D2137; }
.greca-name { color: #4A7A9B; }
.greca-val  { color: #C8D8E8; }

/* Bottone */
.stButton button {
    background: linear-gradient(90deg, #003D6B, #005A9E);
    color: #E8F4FF;
    border: 1px solid #0066CC;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-size: 0.8rem;
    padding: 8px 20px;
    transition: all 0.2s;
}
.stButton button:hover { background: linear-gradient(90deg, #005A9E, #0080CC); border-color: #00AAFF; }

/* Separatore */
hr { border-color: #0D2137; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FASE 1 – MOTORE MATEMATICO
# ═══════════════════════════════════════════════════════════

@dataclass
class OpzioneParams:
    """Contenitore parametri opzione."""
    S: float     # Prezzo Spot sottostante
    K: float     # Strike price
    T: float     # Tempo alla scadenza (anni)
    r: float     # Tasso risk-free (annuo, decimale)
    sigma: float # Volatilità Implicita (annua, decimale)
    tipo: str = "put"  # "put" o "call"


def d1_d2(params: OpzioneParams):
    """Calcola d1 e d2 del modello Black-Scholes."""
    S, K, T, r, sigma = params.S, params.K, params.T, params.r, params.sigma
    if T <= 0 or sigma <= 0:
        return 0.0, 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def black_scholes_prezzo(params: OpzioneParams) -> float:
    """
    Calcola il prezzo teorico dell'opzione (Put o Call) con Black-Scholes.
    Ritorna il premio in unità di valuta del sottostante.
    """
    S, K, T, r = params.S, params.K, params.T, params.r
    d1, d2 = d1_d2(params)

    if params.tipo == "call":
        prezzo = S * si.norm.cdf(d1) - K * np.exp(-r * T) * si.norm.cdf(d2)
    else:  # put
        prezzo = K * np.exp(-r * T) * si.norm.cdf(-d2) - S * si.norm.cdf(-d1)

    return max(prezzo, 0.0)


def probabilita_successo_put(params: OpzioneParams) -> float:
    """
    Probabilità che la Put scada OTM (S > K a scadenza).
    Equivale a N(d2) con la metrica risk-neutral.
    """
    _, d2 = d1_d2(params)
    return si.norm.cdf(d2)  # P(S_T > K) in misura risk-neutral


def calcola_greche(params: OpzioneParams) -> dict:
    """
    Calcola le greche principali per una Put Short:
      - Delta  : sensibilità al prezzo (≈ probabilità ITM con segno)
      - Gamma  : variazione del Delta
      - Theta  : decadimento temporale giornaliero
      - Vega   : sensibilità alla volatilità
      - Rho    : sensibilità al tasso
    """
    S, K, T, r, sigma = params.S, params.K, params.T, params.r, params.sigma
    if T <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}

    d1, d2 = d1_d2(params)
    pdf_d1 = si.norm.pdf(d1)
    cdf_neg_d1 = si.norm.cdf(-d1)
    cdf_neg_d2 = si.norm.cdf(-d2)

    # Delta Put: -N(-d1)  →  valore negativo per long, positivo per short
    delta = -cdf_neg_d1

    # Gamma (identico per call e put)
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))

    # Theta Put (per anno → diviso 365 per giorno)
    theta = (
        -(S * pdf_d1 * sigma) / (2 * np.sqrt(T))
        + r * K * np.exp(-r * T) * cdf_neg_d2
    ) / 365

    # Vega (per 1% di variazione IV)
    vega = S * pdf_d1 * np.sqrt(T) / 100

    # Rho Put
    rho = -K * T * np.exp(-r * T) * cdf_neg_d2 / 100

    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 6),
        "theta": round(theta, 4),
        "vega":  round(vega, 4),
        "rho":   round(rho, 4),
    }


# ═══════════════════════════════════════════════════════════
# FASE 2 – LOGICA DI SELEZIONE
# ═══════════════════════════════════════════════════════════

def semaforo_iv(iv_corrente: float, iv_media_storica: float) -> dict:
    """
    Analizza l'Implied Volatility rispetto alla media storica.
    Ritorna: colore semaforo, descrizione, fattore moltiplicativo IV rank.
    """
    ratio = iv_corrente / iv_media_storica if iv_media_storica > 0 else 1.0

    if ratio >= 1.25:
        return {"colore": "green", "label": "IV ELEVATA ✓", "dettaglio": f"IV {ratio:.1%} vs media – Condizioni favorevoli per la vendita"}
    elif ratio >= 0.85:
        return {"colore": "yellow", "label": "IV NELLA NORMA ≈", "dettaglio": f"IV {ratio:.1%} vs media – Valutare attentamente il premio"}
    else:
        return {"colore": "red", "label": "IV BASSA ✗", "dettaglio": f"IV {ratio:.1%} vs media – Premio insufficiente, evitare la vendita"}


def suggerisci_strike(
    S: float,
    sigma: float,
    T: float,
    r: float,
    prob_target: float = 0.95
) -> float:
    """
    Trova lo strike che garantisce la probabilità di successo desiderata.
    Usa l'inverso della distribuzione log-normale:
        K = S * exp((r - 0.5*σ²)*T - σ*√T * N⁻¹(1 - prob_target))
    """
    if T <= 0 or sigma <= 0:
        return S
    z = si.norm.ppf(1.0 - prob_target)   # quantile negativo
    K = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    return round(K, 2)


# ═══════════════════════════════════════════════════════════
# FASE 3 – GESTIONE DEL RISCHIO
# ═══════════════════════════════════════════════════════════

def position_sizing(
    capitale: float,
    strike: float,
    margine_perc: float = 0.15,
    moltiplicatore: int = 100
) -> dict:
    """
    Calcola il numero massimo di contratti Short Put vendibili.
    Ogni contratto copre 'moltiplicatore' azioni (standard: 100).
    """
    margine_per_contratto = strike * moltiplicatore * (margine_perc / 100)
    n_contratti = int(capitale // margine_per_contratto) if margine_per_contratto > 0 else 0
    capitale_impegnato = n_contratti * margine_per_contratto
    capitale_libero = capitale - capitale_impegnato

    return {
        "n_contratti":         n_contratti,
        "margine_per_contratto": round(margine_per_contratto, 2),
        "capitale_impegnato":  round(capitale_impegnato, 2),
        "capitale_libero":     round(capitale_libero, 2),
    }


def worst_case_scenario(
    S: float,
    strike: float,
    premio_incassato: float,
    n_contratti: int,
    crash_perc: float = 20.0,
    moltiplicatore: int = 100
) -> dict:
    """
    Scenario peggiore: crollo istantaneo del sottostante del crash_perc%.
    Calcola la perdita massima stimata al netto del premio incassato.
    """
    S_crash = S * (1 - crash_perc / 100)
    perdita_per_contratto = max(strike - S_crash, 0) - premio_incassato
    perdita_totale = perdita_per_contratto * n_contratti * moltiplicatore
    premio_totale_incassato = premio_incassato * n_contratti * moltiplicatore

    return {
        "S_crash":              round(S_crash, 2),
        "perdita_per_contratto": round(perdita_per_contratto, 2),
        "perdita_totale":       round(perdita_totale, 2),
        "premio_totale_incassato": round(premio_totale_incassato, 2),
        "crash_perc":           crash_perc,
    }


# ═══════════════════════════════════════════════════════════
# FASE 4 – INTERFACCIA UTENTE STREAMLIT
# ═══════════════════════════════════════════════════════════

def grafico_pnl(
    S: float,
    strike: float,
    premio: float,
    n_contratti: int,
    moltiplicatore: int = 100
) -> go.Figure:
    """
    Genera il grafico interattivo del P&L a scadenza per una Short Put.
    """
    # Range prezzi: dal -40% al +20% rispetto allo spot
    prezzi = np.linspace(S * 0.55, S * 1.20, 300)
    pnl_per_share = np.where(prezzi < strike, prezzi - strike + premio, premio)
    pnl_totale = pnl_per_share * n_contratti * moltiplicatore

    # Colorazione area profitto/perdita
    colori = ["#2ECC71" if v >= 0 else "#E74C3C" for v in pnl_totale]

    fig = go.Figure()

    # Area sotto la curva
    fig.add_trace(go.Scatter(
        x=prezzi, y=pnl_totale,
        fill='tozeroy',
        fillcolor='rgba(46, 204, 113, 0.08)',
        line=dict(color='#2ECC71', width=2),
        name='P&L Totale',
        hovertemplate='Spot: %{x:.2f}<br>P&L: %{y:,.0f} €<extra></extra>',
    ))

    # Linea zero
    fig.add_hline(y=0, line=dict(color='#C8D8E8', dash='dot', width=1))

    # Linea Strike
    fig.add_vline(x=strike, line=dict(color='#F39C12', dash='dash', width=1.5),
                  annotation_text=f"Strike {strike:.1f}", annotation_font_color="#F39C12")

    # Linea Spot corrente
    fig.add_vline(x=S, line=dict(color='#00D4FF', dash='dash', width=1.5),
                  annotation_text=f"Spot {S:.1f}", annotation_font_color="#00D4FF")

    fig.update_layout(
        paper_bgcolor='#050A0F',
        plot_bgcolor='#071828',
        font=dict(family='Share Tech Mono', size=11, color='#C8D8E8'),
        title=dict(text='PROFILO P&L A SCADENZA — SHORT PUT', font=dict(size=13, color='#5EAAD7')),
        xaxis=dict(
            title='Prezzo Sottostante a Scadenza',
            gridcolor='#0D2137', zerolinecolor='#1A3A55',
        ),
        yaxis=dict(
            title='P&L (€)',
            gridcolor='#0D2137', zerolinecolor='#1A3A55',
        ),
        hovermode='x unified',
        legend=dict(bgcolor='#071828', bordercolor='#0D2137'),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────
# INTESTAZIONE
# ─────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.markdown("""
    <div style='padding: 10px 0 5px 0;'>
        <span style='font-family: Share Tech Mono; font-size:0.75rem; color:#4A7A9B; letter-spacing:0.2em;'>PLUTONIS QUANTITATIVE SYSTEMS</span><br>
        <span style='font-family: Rajdhani; font-size:2.4rem; font-weight:700; color:#E8F4FF; letter-spacing:0.04em;'>⚡ OPTIONS QUANT DASHBOARD</span><br>
        <span style='font-family: Share Tech Mono; font-size:0.72rem; color:#4A7A9B;'>SHORT PUT SELLER — MOTORE BLACK-SCHOLES v1.0</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# ─────────────────────────────────────────────────────────
# SIDEBAR – INPUT UTENTE
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📐 PARAMETRI DI MERCATO")

    spot = st.number_input(
        "Prezzo Spot Sottostante (S)",
        min_value=1.0, max_value=100_000.0, value=5_000.0, step=10.0,
        help="Prezzo corrente del sottostante (es. indice S&P500, azione)"
    )

    dte = st.slider(
        "Giorni alla Scadenza (DTE)",
        min_value=1, max_value=365, value=30,
        help="Days To Expiration — numero di giorni calendariali"
    )

    iv_corrente = st.slider(
        "Volatilità Implicita — IV (%)",
        min_value=1.0, max_value=150.0, value=20.0, step=0.5,
        help="Volatilità implicita dell'opzione in percentuale annua"
    )

    iv_media_storica = st.slider(
        "IV Media Storica (%)",
        min_value=1.0, max_value=100.0, value=15.0, step=0.5,
        help="Media storica dell'IV per confronto con il semaforo"
    )

    r = st.number_input(
        "Tasso Risk-Free (%)",
        min_value=0.0, max_value=20.0, value=4.5, step=0.1,
        help="Tasso di interesse privo di rischio annuo"
    )

    st.divider()
    st.markdown("### 💼 MONEY MANAGEMENT")

    capitale = st.number_input(
        "Capitale Disponibile (€)",
        min_value=1_000.0, max_value=10_000_000.0, value=50_000.0, step=1_000.0
    )

    margine_perc = st.slider(
        "Margine Richiesto (% dello Strike)",
        min_value=5.0, max_value=50.0, value=15.0, step=1.0,
        help="Percentuale dello strike richiesta come margine dal broker"
    )

    crash_perc = st.slider(
        "Scenario Crash (%)",
        min_value=5.0, max_value=50.0, value=20.0, step=1.0,
        help="Percentuale di crollo per lo scenario peggiore"
    )

    st.divider()
    st.markdown("### 🎯 STRATEGIA")

    prob_target = st.slider(
        "Probabilità di Successo Target (%)",
        min_value=70.0, max_value=99.0, value=90.0, step=1.0,
        help="Lo strike consigliato raggiungerà questa probabilità di scadere OTM"
    )

    # Mock Data / API Toggle
    usa_mock = st.toggle("Usa Mock Data (demo)", value=True, help="OFF = integrazione futura con yfinance")
    if not usa_mock:
        st.info("⚙️ Integrazione yfinance: aggiungi `import yfinance as yf` e popola i campi con `ticker.option_chain()`")


# ─────────────────────────────────────────────────────────
# CALCOLI CENTRALI
# ─────────────────────────────────────────────────────────
T_anni = dte / 365.0
sigma_dec = iv_corrente / 100.0
r_dec = r / 100.0

strike_consigliato = suggerisci_strike(spot, sigma_dec, T_anni, r_dec, prob_target / 100.0)

params = OpzioneParams(S=spot, K=strike_consigliato, T=T_anni, r=r_dec, sigma=sigma_dec)
premio = black_scholes_prezzo(params)
prob_successo = probabilita_successo_put(params)
greche = calcola_greche(params)
iv_info = semaforo_iv(iv_corrente, iv_media_storica)
sizing = position_sizing(capitale, strike_consigliato, margine_perc)
wcs = worst_case_scenario(spot, strike_consigliato, premio, sizing["n_contratti"], crash_perc)


# ─────────────────────────────────────────────────────────
# SEMAFORO IV
# ─────────────────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex; align-items:center; margin-bottom:20px; padding: 12px 20px;
     background:#071828; border:1px solid #0D2137; border-radius:8px;'>
    <span class='semaforo {iv_info["colore"]}'></span>
    <span style='font-family:Share Tech Mono; font-size:0.82rem; color:#E8F4FF; margin-right:16px;'>
        IV RANK: {iv_info["label"]}
    </span>
    <span style='font-family:Rajdhani; font-size:0.9rem; color:#7EC8E3;'>
        {iv_info["dettaglio"]}
    </span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# 3 COLONNE PRINCIPALI
# ─────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>🎯 STRIKE CONSIGLIATO</div>
        <div class='metric-value'>{strike_consigliato:,.1f}</div>
        <div class='metric-delta'>Distanza dallo Spot: {((spot - strike_consigliato)/spot*100):.1f}% OTM</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    colore_prob = "danger" if prob_successo < 0.80 else ("warning" if prob_successo < 0.90 else "")
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>✅ PROBABILITÀ DI SUCCESSO</div>
        <div class='metric-value' style='color:{"#2ECC71" if prob_successo>=0.90 else "#F39C12" if prob_successo>=0.80 else "#E74C3C"}'>{prob_successo*100:.1f}%</div>
        <div class='metric-delta {colore_prob}'>P(scade OTM) — modello risk-neutral</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    premio_totale = premio * sizing["n_contratti"] * 100
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>💰 PREMIO STIMATO</div>
        <div class='metric-value'>{premio:.2f}</div>
        <div class='metric-delta'>Totale ({sizing["n_contratti"]} contratti): {premio_totale:,.0f} €/mese</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# GRAFICO P&L
# ─────────────────────────────────────────────────────────
st.plotly_chart(
    grafico_pnl(spot, strike_consigliato, premio, sizing["n_contratti"]),
    use_container_width=True
)


# ─────────────────────────────────────────────────────────
# GRECHE + POSITION SIZING + WORST CASE
# ─────────────────────────────────────────────────────────
g_col, ps_col, wc_col = st.columns(3)

with g_col:
    st.markdown("## GRECHE")
    delta_pct = abs(greche['delta']) * 100
    st.markdown(f"""
    <div class='greche-box'>
        <div class='grecа-row'><span class='greca-name'>Δ DELTA</span><span class='greca-val'>{greche['delta']:.4f} ({delta_pct:.1f}% ITM)</span></div>
        <div class='grecа-row'><span class='greca-name'>Γ GAMMA</span><span class='greca-val'>{greche['gamma']:.6f}</span></div>
        <div class='grecа-row'><span class='greca-name'>Θ THETA</span><span class='greca-val'>+{abs(greche['theta']):.4f} €/giorno</span></div>
        <div class='grecа-row'><span class='greca-name'>ν VEGA</span><span class='greca-val'>{greche['vega']:.4f} / 1% IV</span></div>
        <div class='grecа-row'><span class='greca-name'>ρ RHO</span><span class='greca-val'>{greche['rho']:.4f}</span></div>
    </div>
    """, unsafe_allow_html=True)

with ps_col:
    st.markdown("## POSITION SIZING")
    st.markdown(f"""
    <div class='greche-box'>
        <div class='grecа-row'><span class='greca-name'>CONTRATTI MAX</span><span class='greca-val' style='color:#00D4FF; font-size:1.1rem'>{sizing["n_contratti"]}</span></div>
        <div class='grecа-row'><span class='greca-name'>MARGINE/CONTRATTO</span><span class='greca-val'>{sizing["margine_per_contratto"]:,.0f} €</span></div>
        <div class='grecа-row'><span class='greca-name'>CAPITALE IMPEGNATO</span><span class='greca-val'>{sizing["capitale_impegnato"]:,.0f} €</span></div>
        <div class='grecа-row'><span class='greca-name'>CAPITALE LIBERO</span><span class='greca-val' style='color:#2ECC71'>{sizing["capitale_libero"]:,.0f} €</span></div>
        <div class='grecа-row'><span class='greca-name'>RENDIMENTO THETA/DIE</span><span class='greca-val'>+{abs(greche["theta"]) * sizing["n_contratti"] * 100:,.0f} €</span></div>
    </div>
    """, unsafe_allow_html=True)

with wc_col:
    st.markdown("## WORST CASE SCENARIO")
    st.markdown(f"""
    <div class='worst-case-box'>
        <div style='font-family:Share Tech Mono; font-size:0.7rem; color:#E74C3C; letter-spacing:0.15em; margin-bottom:12px;'>
            ⚠ CROLLO -{wcs["crash_perc"]:.0f}% IN UN GIORNO
        </div>
        <div class='grecа-row' style='border-bottom:1px solid #3A1515;'>
            <span class='greca-name'>SPOT POST-CRASH</span>
            <span class='greca-val'>{wcs["S_crash"]:,.1f}</span>
        </div>
        <div class='grecа-row' style='border-bottom:1px solid #3A1515;'>
            <span class='greca-name'>PERDITA/CONTRATTO</span>
            <span class='greca-val' style='color:#E74C3C'>{wcs["perdita_per_contratto"]:,.0f} €</span>
        </div>
        <div class='grecа-row' style='border-bottom:1px solid #3A1515;'>
            <span class='greca-name'>PERDITA TOTALE</span>
            <span class='greca-val' style='color:#E74C3C; font-size:1.1rem'>{wcs["perdita_totale"]:,.0f} €</span>
        </div>
        <div class='grecа-row'>
            <span class='greca-name'>PREMI INCASSATI</span>
            <span class='greca-val' style='color:#2ECC71'>+{wcs["premio_totale_incassato"]:,.0f} €</span>
        </div>
        <div style='margin-top:12px; font-family:Share Tech Mono; font-size:0.7rem; color:#4A7A9B;'>
            Perdita netta: {wcs["perdita_totale"] + wcs["premio_totale_incassato"]:,.0f} €
            ({((wcs["perdita_totale"] + wcs["premio_totale_incassato"])/capitale*100):.1f}% del capitale)
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# RIEPILOGO SETUP TRADE
# ─────────────────────────────────────────────────────────
st.divider()
st.markdown("## RIEPILOGO TRADE")

setup_data = {
    "Parametro": [
        "Sottostante (Spot)", "Strike Consigliato", "DTE", "IV Corrente",
        "Premio per Contratto", "Contratti", "Premi Totali Mensili",
        "Margine Totale", "Break-Even a Scadenza", "Theta Giornaliero Totale"
    ],
    "Valore": [
        f"{spot:,.2f}", f"{strike_consigliato:,.2f}", f"{dte} gg",
        f"{iv_corrente:.1f}%", f"{premio:.4f} ({premio*100:.2f} €/contratto)",
        str(sizing["n_contratti"]),
        f"{premio * sizing['n_contratti'] * 100:,.0f} €",
        f"{sizing['capitale_impegnato']:,.0f} €",
        f"{strike_consigliato - premio:.2f}",
        f"+{abs(greche['theta']) * sizing['n_contratti'] * 100:,.0f} €/giorno"
    ],
}
df_setup = pd.DataFrame(setup_data)

st.dataframe(
    df_setup,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Parametro": st.column_config.TextColumn(width="medium"),
        "Valore": st.column_config.TextColumn(width="medium"),
    }
)


# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; margin-top:40px; padding:16px;
     font-family:Share Tech Mono; font-size:0.65rem; color:#1A3A55; letter-spacing:0.15em;'>
    PLUTONIS QUANTITATIVE SYSTEMS — SOLO SCOPI EDUCATIVI — NON COSTITUISCE CONSULENZA FINANZIARIA<br>
    ⚙ Predisposto per integrazione API yfinance | Black-Scholes Engine v1.0
</div>
""", unsafe_allow_html=True)
