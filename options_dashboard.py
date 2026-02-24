"""
╔══════════════════════════════════════════════════════════╗
║         PHINANCE - Dashboard Vendita Put                 ║
║         Motore Quantitativo per Short Put Seller         ║
╚══════════════════════════════════════════════════════════╝

Librerie richieste:
    pip install streamlit numpy pandas scipy plotly yfinance

Avvio:
    streamlit run options_dashboard.py
"""

import numpy as np
import pandas as pd
import scipy.stats as si
import streamlit as st
import plotly.graph_objects as go
from dataclasses import dataclass

# Importazione yfinance con gestione errore
try:
    import yfinance as yf
    YFINANCE_DISPONIBILE = True
except ImportError:
    YFINANCE_DISPONIBILE = False

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
# CSS PERSONALIZZATO
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #050A0F;
    color: #C8D8E8;
    font-family: 'Rajdhani', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07111B 0%, #050A0F 100%);
    border-right: 1px solid #0D2137;
}
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #5EAAD7 !important;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
h1 { font-family: 'Rajdhani', sans-serif; font-weight: 700; color: #E8F4FF; }
h2 { font-family: 'Rajdhani', sans-serif; color: #5EAAD7; border-bottom: 1px solid #0D2137; padding-bottom: 4px; }

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
.metric-delta { font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: #2ECC71; margin-top: 4px; }

.semaforo {
    display: inline-block;
    width: 14px; height: 14px;
    border-radius: 50%;
    margin-right: 8px;
    vertical-align: middle;
}
.semaforo.verde  { background: #2ECC71; box-shadow: 0 0 10px #2ECC71; }
.semaforo.giallo { background: #F39C12; box-shadow: 0 0 10px #F39C12; }
.semaforo.rosso  { background: #E74C3C; box-shadow: 0 0 10px #E74C3C; }

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
.riga { display: flex; justify-content: space-between; border-bottom: 1px solid #0D2137; }
.nome { color: #4A7A9B; }
.valore { color: #C8D8E8; }

.info-box {
    background: #071828;
    border: 1px solid #0D2137;
    border-left: 4px solid #00C4FF;
    border-radius: 6px;
    padding: 12px 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #5EAAD7;
    margin-bottom: 16px;
}
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
    width: 100%;
}
hr { border-color: #0D2137; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FUNZIONI YFINANCE — Recupero dati reali
# ═══════════════════════════════════════════════════════════

TICKER_DISPONIBILI = {
    "S&P 500 (SPY)":             "SPY",
    "S&P 500 Indice (^GSPC)":    "^GSPC",
    "NASDAQ 100 (QQQ)":          "QQQ",
    "Dow Jones (^DJI)":          "^DJI",
    "Apple (AAPL)":              "AAPL",
    "Tesla (TSLA)":              "TSLA",
    "Nvidia (NVDA)":             "NVDA",
    "Microsoft (MSFT)":          "MSFT",
    "Amazon (AMZN)":             "AMZN",
    "Altro (inserisci manualmente)": "MANUALE",
}

@st.cache_data(ttl=300)
def recupera_dati_mercato(ticker: str) -> dict:
    """
    Recupera da Yahoo Finance tramite yfinance:
    - Prezzo Spot corrente
    - Volatilità Storica 30 giorni annualizzata
    - Variazione % giornaliera
    - Nome esteso del titolo
    """
    try:
        strumento = yf.Ticker(ticker)
        storico = strumento.history(period="60d")

        if storico.empty:
            return {"errore": f"Nessun dato trovato per '{ticker}'. Verifica che il ticker sia corretto."}

        prezzo_spot = float(storico["Close"].iloc[-1])

        variazione_gg = 0.0
        if len(storico) >= 2:
            prezzo_ieri = float(storico["Close"].iloc[-2])
            variazione_gg = ((prezzo_spot - prezzo_ieri) / prezzo_ieri) * 100

        # Volatilità Storica 30gg annualizzata
        rendimenti = np.log(storico["Close"] / storico["Close"].shift(1)).dropna()
        vol_30gg = float(rendimenti.tail(30).std() * np.sqrt(252) * 100)
        vol_60gg = float(rendimenti.std() * np.sqrt(252) * 100)

        try:
            nome = strumento.info.get("longName", ticker)
        except Exception:
            nome = ticker

        return {
            "prezzo_spot":      round(prezzo_spot, 2),
            "variazione_gg":    round(variazione_gg, 2),
            "vol_storica_30gg": round(vol_30gg, 2),
            "vol_storica_60gg": round(vol_60gg, 2),
            "nome":             nome,
            "ultimo_agg":       storico.index[-1].strftime("%d/%m/%Y"),
            "errore":           None,
        }
    except Exception as e:
        return {"errore": f"Errore di connessione: {str(e)}"}


# ═══════════════════════════════════════════════════════════
# MOTORE MATEMATICO — Black-Scholes
# ═══════════════════════════════════════════════════════════

@dataclass
class ParametriOpzione:
    S: float; K: float; T: float; r: float; sigma: float


def calcola_d1_d2(p: ParametriOpzione):
    if p.T <= 0 or p.sigma <= 0:
        return 0.0, 0.0
    d1 = (np.log(p.S / p.K) + (p.r + 0.5 * p.sigma**2) * p.T) / (p.sigma * np.sqrt(p.T))
    return d1, d1 - p.sigma * np.sqrt(p.T)


def prezzo_put(p: ParametriOpzione) -> float:
    d1, d2 = calcola_d1_d2(p)
    return max(p.K * np.exp(-p.r * p.T) * si.norm.cdf(-d2) - p.S * si.norm.cdf(-d1), 0.0)


def probabilita_successo(p: ParametriOpzione) -> float:
    _, d2 = calcola_d1_d2(p)
    return si.norm.cdf(d2)


def calcola_greche(p: ParametriOpzione) -> dict:
    if p.T <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
    d1, d2 = calcola_d1_d2(p)
    pdf_d1 = si.norm.pdf(d1)
    return {
        "delta": round(-si.norm.cdf(-d1), 4),
        "gamma": round(pdf_d1 / (p.S * p.sigma * np.sqrt(p.T)), 6),
        "theta": round((-(p.S * pdf_d1 * p.sigma) / (2 * np.sqrt(p.T)) + p.r * p.K * np.exp(-p.r * p.T) * si.norm.cdf(-d2)) / 365, 4),
        "vega":  round(p.S * pdf_d1 * np.sqrt(p.T) / 100, 4),
        "rho":   round(-p.K * p.T * np.exp(-p.r * p.T) * si.norm.cdf(-d2) / 100, 4),
    }


# ═══════════════════════════════════════════════════════════
# LOGICA DI SELEZIONE
# ═══════════════════════════════════════════════════════════

def semaforo_volatilita(iv: float, vol_storica: float) -> dict:
    ratio = iv / vol_storica if vol_storica > 0 else 1.0
    if ratio >= 1.25:
        return {"colore": "verde",  "etichetta": "CONDIZIONI OTTIME ✓",
                "dettaglio": f"IV ({iv:.1f}%) è {ratio:.0%} della vol. storica — premi gonfiati, ottimo per vendere"}
    elif ratio >= 0.85:
        return {"colore": "giallo", "etichetta": "CONDIZIONI NELLA NORMA ≈",
                "dettaglio": f"IV ({iv:.1f}%) è in linea con la storia — valutare attentamente"}
    else:
        return {"colore": "rosso",  "etichetta": "CONDIZIONI SFAVOREVOLI ✗",
                "dettaglio": f"IV ({iv:.1f}%) è bassa — premi insufficienti, meglio aspettare"}


def suggerisci_strike(S, sigma, T, r, prob_target) -> float:
    if T <= 0 or sigma <= 0:
        return S
    return round(S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * si.norm.ppf(1.0 - prob_target)), 2)


# ═══════════════════════════════════════════════════════════
# GESTIONE DEL RISCHIO
# ═══════════════════════════════════════════════════════════

def calcola_position_sizing(capitale, strike, margine_perc, moltiplicatore=100) -> dict:
    margine_c = strike * moltiplicatore * (margine_perc / 100)
    n = int(capitale // margine_c) if margine_c > 0 else 0
    return {
        "n_contratti":           n,
        "margine_per_contratto": round(margine_c, 2),
        "capitale_impegnato":    round(n * margine_c, 2),
        "capitale_libero":       round(capitale - n * margine_c, 2),
    }


def calcola_scenario_peggiore(S, strike, premio, n_contratti, crash_perc, moltiplicatore=100) -> dict:
    S_crash = S * (1 - crash_perc / 100)
    perdita_c = max(strike - S_crash, 0) - premio
    return {
        "S_crash":               round(S_crash, 2),
        "perdita_per_contratto": round(perdita_c, 2),
        "perdita_totale":        round(perdita_c * n_contratti * moltiplicatore, 2),
        "premio_totale":         round(premio * n_contratti * moltiplicatore, 2),
        "crash_perc":            crash_perc,
    }


# ═══════════════════════════════════════════════════════════
# GRAFICO P&L
# ═══════════════════════════════════════════════════════════

def grafico_pnl(S, strike, premio, n_contratti, moltiplicatore=100) -> go.Figure:
    prezzi = np.linspace(S * 0.55, S * 1.20, 300)
    pnl = np.where(prezzi < strike, prezzi - strike + premio, premio) * n_contratti * moltiplicatore
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prezzi, y=np.maximum(pnl, 0), fill='tozeroy',
        fillcolor='rgba(46,204,113,0.12)', line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=prezzi, y=np.minimum(pnl, 0), fill='tozeroy',
        fillcolor='rgba(231,76,60,0.12)', line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=prezzi, y=pnl, line=dict(color='#00D4FF', width=2.5),
        name='Profitto / Perdita',
        hovertemplate='Prezzo a scadenza: %{x:.2f}<br>P&L: %{y:,.0f} €<extra></extra>'))
    fig.add_vline(x=strike, line=dict(color='#F39C12', dash='dash', width=1.5),
        annotation_text=f"Strike {strike:.0f}", annotation_font_color="#F39C12", annotation_position="top right")
    fig.add_vline(x=S, line=dict(color='#00D4FF', dash='dot', width=1.5),
        annotation_text=f"Prezzo attuale {S:.0f}", annotation_font_color="#00D4FF", annotation_position="top left")
    fig.add_vline(x=strike - premio, line=dict(color='#9B59B6', dash='dash', width=1),
        annotation_text=f"Pareggio {strike-premio:.0f}", annotation_font_color="#9B59B6")
    fig.add_hline(y=0, line=dict(color='#C8D8E8', dash='dot', width=1))
    fig.update_layout(
        paper_bgcolor='#050A0F', plot_bgcolor='#071828',
        font=dict(family='Share Tech Mono', size=11, color='#C8D8E8'),
        title=dict(text='📈 PROFILO PROFITTO / PERDITA A SCADENZA — VENDITA PUT', font=dict(size=13, color='#5EAAD7')),
        xaxis=dict(title='Prezzo del Sottostante a Scadenza', gridcolor='#0D2137'),
        yaxis=dict(title='Profitto / Perdita (€)', gridcolor='#0D2137'),
        hovermode='x unified', margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


# ═══════════════════════════════════════════════════════════
# INTESTAZIONE
# ═══════════════════════════════════════════════════════════

st.markdown("""
<div style='padding: 10px 0 5px 0;'>
    <span style='font-family:Share Tech Mono; font-size:0.75rem; color:#4A7A9B; letter-spacing:0.2em;'>SISTEMI QUANTITATIVI PER IL TRADING DI OPZIONI</span><br>
    <span style='font-family:Rajdhani; font-size:2.6rem; font-weight:700; color:#E8F4FF; letter-spacing:0.04em;'>📊 PHINANCE</span>
    <span style='font-family:Rajdhani; font-size:1.2rem; color:#5EAAD7; margin-left:12px;'>Dashboard Vendita Put</span><br>
    <span style='font-family:Share Tech Mono; font-size:0.72rem; color:#4A7A9B;'>Motore Black-Scholes · Dati Yahoo Finance in Tempo Reale · Gestione del Rischio</span>
</div>
""", unsafe_allow_html=True)

st.divider()


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🔍 SELEZIONE STRUMENTO")

    scelta = st.selectbox("Scegli il sottostante", options=list(TICKER_DISPONIBILI.keys()), index=0,
        help="Seleziona lo strumento su cui vuoi vendere la Put")

    ticker_selezionato = TICKER_DISPONIBILI[scelta]
    if ticker_selezionato == "MANUALE":
        ticker_manuale = st.text_input("Inserisci il ticker (es. AAPL)", value="SPY",
            help="Usa il formato ticker di Yahoo Finance")
        ticker_da_usare = ticker_manuale.upper().strip()
    else:
        ticker_da_usare = ticker_selezionato

    aggiorna = st.button("🔄 AGGIORNA DATI DI MERCATO")

    st.divider()
    st.markdown("### 📐 PARAMETRI OPZIONE")

    dte = st.slider("Giorni alla Scadenza (DTE)", 1, 365, 30,
        help="Numero di giorni calendariali fino alla scadenza")
    iv_corrente = st.slider("Volatilità Implicita — IV (%)", 1.0, 150.0, 20.0, step=0.5,
        help="Inserisci l'IV che vedi sul tuo broker per questa scadenza")
    r = st.number_input("Tasso Risk-Free (%)", 0.0, 20.0, 4.5, step=0.1,
        help="Rendimento BTP/Treasury come riferimento")

    st.divider()
    st.markdown("### 💼 GESTIONE DEL RISCHIO")

    capitale = st.number_input("Capitale Disponibile (€)", 1_000.0, 10_000_000.0, 50_000.0, step=1_000.0)
    margine_perc = st.slider("Margine Richiesto dal Broker (%)", 5.0, 50.0, 15.0, step=1.0,
        help="Percentuale dello strike che il broker blocca come garanzia")
    crash_perc = st.slider("Ipotesi Scenario di Crisi (%)", 5.0, 50.0, 20.0, step=1.0,
        help="Di quanto potrebbe scendere il mercato nel caso peggiore?")

    st.divider()
    st.markdown("### 🎯 OBIETTIVO STRATEGIA")

    prob_target = st.slider("Probabilità di Successo Desiderata (%)", 70.0, 99.0, 90.0, step=1.0,
        help="Lo strike sarà calcolato per garantire questa probabilità di scadere senza perdite")


# ═══════════════════════════════════════════════════════════
# RECUPERO DATI DI MERCATO
# ═══════════════════════════════════════════════════════════

if ("dati" not in st.session_state or aggiorna or
        st.session_state.get("ticker_corrente") != ticker_da_usare):
    with st.spinner(f"⏳ Recupero dati per {ticker_da_usare} da Yahoo Finance..."):
        st.session_state.dati = recupera_dati_mercato(ticker_da_usare)
        st.session_state.ticker_corrente = ticker_da_usare

dati = st.session_state.dati

if dati.get("errore"):
    st.error(f"⚠️ **Errore:** {dati['errore']}")
    st.info("💡 Prova con ticker come: SPY, QQQ, AAPL, TSLA, MSFT, ^GSPC")
    st.stop()

spot         = dati["prezzo_spot"]
vol_storica  = dati["vol_storica_30gg"]
variazione   = dati["variazione_gg"]
nome         = dati["nome"]
ultimo_agg   = dati["ultimo_agg"]


# ═══════════════════════════════════════════════════════════
# CALCOLI
# ═══════════════════════════════════════════════════════════

T_anni = dte / 365.0
sigma  = iv_corrente / 100.0
r_dec  = r / 100.0

strike      = suggerisci_strike(spot, sigma, T_anni, r_dec, prob_target / 100.0)
params      = ParametriOpzione(S=spot, K=strike, T=T_anni, r=r_dec, sigma=sigma)
premio      = prezzo_put(params)
prob_ok     = probabilita_successo(params)
greche      = calcola_greche(params)
semaforo    = semaforo_volatilita(iv_corrente, vol_storica)
sizing      = calcola_position_sizing(capitale, strike, margine_perc)
scenario    = calcola_scenario_peggiore(spot, strike, premio, sizing["n_contratti"], crash_perc)
distanza    = (spot - strike) / spot * 100
premio_tot  = premio * sizing["n_contratti"] * 100
theta_tot   = abs(greche["theta"]) * sizing["n_contratti"] * 100
rend_mese   = (premio_tot / sizing["capitale_impegnato"] * 100) if sizing["capitale_impegnato"] > 0 else 0


# ═══════════════════════════════════════════════════════════
# BARRA INFORMAZIONI STRUMENTO
# ═══════════════════════════════════════════════════════════

colore_v = "#2ECC71" if variazione >= 0 else "#E74C3C"
freccia  = "▲" if variazione >= 0 else "▼"

st.markdown(f"""
<div class='info-box'>
    <span style='color:#E8F4FF; font-size:0.9rem; font-family:Rajdhani; font-weight:700;'>{nome}</span>
    &nbsp;|&nbsp;
    <span style='color:#00D4FF; font-size:1rem; font-family:Rajdhani; font-weight:700;'>{spot:,.2f}</span>
    &nbsp;
    <span style='color:{colore_v};'>{freccia} {abs(variazione):.2f}% oggi</span>
    &nbsp;|&nbsp;
    Volatilità Storica 30gg: <span style='color:#E8F4FF;'>{vol_storica:.1f}%</span>
    &nbsp;|&nbsp;
    Aggiornato al: <span style='color:#E8F4FF;'>{ultimo_agg}</span>
    &nbsp;|&nbsp;
    <span style='color:#4A7A9B;'>Fonte: Yahoo Finance</span>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SEMAFORO VOLATILITÀ
# ═══════════════════════════════════════════════════════════

st.markdown(f"""
<div style='display:flex; align-items:center; margin-bottom:20px; padding:14px 20px;
     background:#071828; border:1px solid #0D2137; border-radius:8px;'>
    <span class='semaforo {semaforo["colore"]}'></span>
    <span style='font-family:Share Tech Mono; font-size:0.82rem; color:#E8F4FF; margin-right:16px;'>
        SEGNALE: {semaforo["etichetta"]}
    </span>
    <span style='font-family:Rajdhani; font-size:0.95rem; color:#7EC8E3;'>
        {semaforo["dettaglio"]}
    </span>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# 3 METRICHE PRINCIPALI
# ═══════════════════════════════════════════════════════════

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>🎯 STRIKE CONSIGLIATO</div>
        <div class='metric-value'>{strike:,.1f}</div>
        <div class='metric-delta'>Distanza dal prezzo attuale: {distanza:.1f}% sotto</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    colore_p = "#2ECC71" if prob_ok >= 0.90 else "#F39C12" if prob_ok >= 0.80 else "#E74C3C"
    giudizio = "Eccellente" if prob_ok >= 0.90 else "Accettabile" if prob_ok >= 0.80 else "Rischiosa"
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>✅ PROBABILITÀ DI SUCCESSO</div>
        <div class='metric-value' style='color:{colore_p};'>{prob_ok*100:.1f}%</div>
        <div class='metric-delta'>Valutazione: {giudizio} — probabilità che scada senza perdite</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>💰 PREMIO INCASSATO</div>
        <div class='metric-value'>{premio:.2f}</div>
        <div class='metric-delta'>Totale con {sizing["n_contratti"]} contratti: +{premio_tot:,.0f} € al mese</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# GRAFICO P&L
# ═══════════════════════════════════════════════════════════

st.plotly_chart(grafico_pnl(spot, strike, premio, sizing["n_contratti"]), use_container_width=True)


# ═══════════════════════════════════════════════════════════
# PANNELLI INFERIORI
# ═══════════════════════════════════════════════════════════

col_g, col_ps, col_wc = st.columns(3)

with col_g:
    st.markdown("## LETTERE GRECHE")
    st.markdown("<div class='info-box' style='font-size:0.68rem;'>Le greche misurano la sensibilità del prezzo dell'opzione alle variazioni di mercato</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='greche-box'>
        <div class='riga'><span class='nome'>Δ DELTA (prob. ITM)</span><span class='valore'>{greche['delta']:.4f} → {abs(greche['delta'])*100:.1f}%</span></div>
        <div class='riga'><span class='nome'>Γ GAMMA (accelerazione)</span><span class='valore'>{greche['gamma']:.6f}</span></div>
        <div class='riga'><span class='nome'>Θ THETA (guadagno/giorno)</span><span class='valore' style='color:#2ECC71'>+{abs(greche['theta']):.4f} €</span></div>
        <div class='riga'><span class='nome'>ν VEGA (sensib. volatilità)</span><span class='valore'>{greche['vega']:.4f} per 1% IV</span></div>
        <div class='riga'><span class='nome'>ρ RHO (sensib. tassi)</span><span class='valore'>{greche['rho']:.4f}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_ps:
    st.markdown("## DIMENSIONE POSIZIONE")
    st.markdown("<div class='info-box' style='font-size:0.68rem;'>Quanti contratti puoi vendere in sicurezza con il tuo capitale disponibile</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='greche-box'>
        <div class='riga'><span class='nome'>CONTRATTI MASSIMI</span><span class='valore' style='color:#00D4FF; font-size:1.1rem'>{sizing["n_contratti"]}</span></div>
        <div class='riga'><span class='nome'>MARGINE PER CONTRATTO</span><span class='valore'>{sizing["margine_per_contratto"]:,.0f} €</span></div>
        <div class='riga'><span class='nome'>CAPITALE BLOCCATO</span><span class='valore'>{sizing["capitale_impegnato"]:,.0f} €</span></div>
        <div class='riga'><span class='nome'>CAPITALE LIBERO</span><span class='valore' style='color:#2ECC71'>{sizing["capitale_libero"]:,.0f} €</span></div>
        <div class='riga'><span class='nome'>GUADAGNO THETA/GIORNO</span><span class='valore' style='color:#2ECC71'>+{theta_tot:,.0f} €</span></div>
        <div class='riga'><span class='nome'>RENDIMENTO SUL MARGINE</span><span class='valore' style='color:#2ECC71'>{rend_mese:.1f}% / mese</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_wc:
    st.markdown("## SCENARIO DI CRISI")
    st.markdown("<div class='info-box' style='font-size:0.68rem; border-left-color:#E74C3C;'>Cosa succederebbe se il mercato crollasse improvvisamente</div>", unsafe_allow_html=True)
    perdita_netta = scenario["perdita_totale"] + scenario["premio_totale"]
    impatto = (perdita_netta / capitale * 100) if capitale > 0 else 0
    st.markdown(f"""
    <div class='worst-case-box'>
        <div style='font-family:Share Tech Mono; font-size:0.7rem; color:#E74C3C; margin-bottom:12px;'>
            ⚠ IPOTESI: CROLLO DEL -{scenario["crash_perc"]:.0f}% IN UN GIORNO
        </div>
        <div class='riga' style='border-bottom:1px solid #3A1515;'><span class='nome'>PREZZO DOPO IL CROLLO</span><span class='valore'>{scenario["S_crash"]:,.2f}</span></div>
        <div class='riga' style='border-bottom:1px solid #3A1515;'><span class='nome'>PERDITA PER CONTRATTO</span><span class='valore' style='color:#E74C3C'>{scenario["perdita_per_contratto"]:,.0f} €</span></div>
        <div class='riga' style='border-bottom:1px solid #3A1515;'><span class='nome'>PERDITA LORDA TOTALE</span><span class='valore' style='color:#E74C3C'>{scenario["perdita_totale"]:,.0f} €</span></div>
        <div class='riga' style='border-bottom:1px solid #3A1515;'><span class='nome'>PREMI GIÀ INCASSATI</span><span class='valore' style='color:#2ECC71'>+{scenario["premio_totale"]:,.0f} €</span></div>
        <div class='riga'><span class='nome'>PERDITA NETTA FINALE</span><span class='valore' style='color:#E74C3C; font-weight:bold'>{perdita_netta:,.0f} €</span></div>
        <div style='margin-top:10px; font-family:Share Tech Mono; font-size:0.7rem; color:#4A7A9B;'>
            Impatto sul capitale totale: {impatto:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# RIEPILOGO OPERAZIONE
# ═══════════════════════════════════════════════════════════

st.divider()
st.markdown("## 📋 RIEPILOGO OPERAZIONE")

st.dataframe(pd.DataFrame({
    "Parametro": [
        "Strumento", "Prezzo Attuale", "Strike Consigliato", "Distanza Strike",
        "Giorni alla Scadenza", "Volatilità Implicita (IV)", "Volatilità Storica 30gg",
        "Premio per Contratto", "Numero di Contratti", "Incasso Totale Premi",
        "Punto di Pareggio a Scadenza", "Guadagno Theta Giornaliero", "Rendimento Mensile sul Margine"
    ],
    "Valore": [
        nome, f"{spot:,.2f}", f"{strike:,.2f}",
        f"{distanza:.1f}% sotto il prezzo attuale",
        f"{dte} giorni", f"{iv_corrente:.1f}%", f"{vol_storica:.1f}%",
        f"{premio:.4f}  ({premio*100:.2f} € per contratto da 100 azioni)",
        str(sizing["n_contratti"]),
        f"+{premio_tot:,.0f} €",
        f"{strike - premio:,.2f}",
        f"+{theta_tot:,.0f} € al giorno",
        f"{rend_mese:.1f}%  ({rend_mese*12:.1f}% annuo stimato)",
    ],
}), use_container_width=True, hide_index=True,
    column_config={
        "Parametro": st.column_config.TextColumn("Parametro", width="medium"),
        "Valore":    st.column_config.TextColumn("Valore",    width="large"),
    }
)


# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════

st.markdown("""
<div style='text-align:center; margin-top:40px; padding:16px;
     font-family:Share Tech Mono; font-size:0.65rem; color:#1A3A55; letter-spacing:0.12em;'>
    PHINANCE · SISTEMI QUANTITATIVI PER IL TRADING DI OPZIONI<br>
    SOLO A SCOPO EDUCATIVO — NON COSTITUISCE CONSULENZA FINANZIARIA<br>
    Dati forniti da Yahoo Finance · Black-Scholes Engine v2.0
</div>
""", unsafe_allow_html=True)
