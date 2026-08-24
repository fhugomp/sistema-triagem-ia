"""
Componentes de interface Streamlit para o Sistema de Triagem.
Funcoes puras de renderizacao que recebem dados tipados e escrevem na tela.
Suporta internacionalizacao via dicionario de traducoes (i18n).
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Any, Dict, List, Tuple

from src.models.paciente import Paciente
from src.simulation.runner import ResultadoSimulacao
from src.utils import gerar_dataframe_auditoria

# ---------------------------------------------------------------------------
# CSS Global — Dark Premium SaaS Theme
# ---------------------------------------------------------------------------

CSS_GLOBAL = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Typography */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* 1. LIMITE DE LARGURA DA TELA (1100px) E CENTRALIZACAO */
    [data-testid="block-container"] {
        max-width: 1100px !important;
        margin: 0 auto !important;
        padding-top: 1.5rem !important;
    }

    /* Esconde o header padrao do Streamlit */
    [data-testid="stHeader"] { display: none !important; }

    /* Subtle radial glow behind hero area */
    .block-container::before {
        content: '';
        position: fixed; top: 0; left: 0; width: 100%; height: 60vh;
        background: radial-gradient(ellipse at 50% -10%, rgba(139,92,246,0.07), transparent 55%);
        pointer-events: none; z-index: 0;
    }

    /* Kill sidebar entirely */
    section[data-testid="stSidebar"]         { display: none !important; }
    div[data-testid="collapsedControl"]      { display: none !important; }
    button[data-testid="baseButton-headerNoPadding"] { display: none !important; }

    /* Widget label size increase */
    div[data-testid="stSlider"] label,
    div[data-testid="stRadio"]  label,
    div[data-testid="stRadio"] > label {
        font-size: 14px !important; font-weight: 500 !important;
        color: #8b93a7 !important; letter-spacing: 0.3px !important;
    }

    /* 2. NAVBAR CAPSULA (Usando DOM real do Streamlit) */
    
    /* A) A linha inteira da navbar */
    [data-testid="stHorizontalBlock"]:has(.logo-container) {
        position: sticky !important;
        top: 18px !important;
        z-index: 999 !important;
        margin-bottom: 56px !important; /* Espacamento visual de 50-60px ate o Hero */
    }

    /* Logo */
    .logo-container {
        font-size: 21px;
        font-weight: 700;
        letter-spacing: 1.8px;
        background: linear-gradient(90deg, #8B5CF6, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'Inter', sans-serif;
        white-space: nowrap;
    }

    /* B) Capsula central (utilizando o marcador nav-capsule-marker) */
    [data-testid="stVerticalBlock"]:has(.nav-capsule-marker) > [data-testid="stHorizontalBlock"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: rgba(16, 19, 26, 0.78) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 999px !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        padding: 5px !important;
        gap: 5px !important;
        width: fit-content !important;
        margin: 0 auto !important;
    }

    /* C) Links da Capsula */
    [data-testid="stVerticalBlock"]:has(.nav-capsule-marker) [data-testid="stPageLink"] {
        display: flex;
        align-items: center;
    }

    [data-testid="stVerticalBlock"]:has(.nav-capsule-marker) [data-testid="stPageLink"] a {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 9px 14px !important;
        min-height: 36px !important;
        color: #8B93A7 !important;
        text-decoration: none !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.7px !important;
        border-radius: 999px !important;
        background: transparent !important;
        transition: color 0.25s ease, background 0.25s ease, box-shadow 0.25s ease !important;
        text-transform: uppercase !important;
        white-space: nowrap;
    }

    [data-testid="stVerticalBlock"]:has(.nav-capsule-marker) [data-testid="stPageLink"] a:hover {
        color: #F5F7FA !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }

    [data-testid="stVerticalBlock"]:has(.nav-capsule-marker) [data-testid="stPageLink"] a[aria-current="page"] {
        color: #F5F7FA !important;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.18), rgba(6, 182, 212, 0.08)) !important;
        box-shadow: inset 0 0 0 1px rgba(139, 92, 246, 0.15) !important;
    }

    /* Indicador visual da pagina ativa */
    [data-testid="stVerticalBlock"]:has(.nav-capsule-marker) [data-testid="stPageLink"] a[aria-current="page"]::after {
        content: '';
        position: absolute;
        bottom: 4px;
        left: 50%;
        transform: translateX(-50%);
        width: 18px;
        height: 2px;
        border-radius: 999px;
        background: linear-gradient(90deg, #8B5CF6, #06B6D4);
    }

    /* D) Botao de Idioma (utilizando o marcador lang-btn-marker) */
    [data-testid="stColumn"]:has(.lang-btn-marker) [data-testid="stVerticalBlock"] > div:last-child {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }

    [data-testid="stVerticalBlock"]:has(.lang-btn-marker) [data-testid="stButton"] button {
        min-height: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        width: 40px !important;
        padding: 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        background: rgba(16, 19, 26, 0.78) !important;
        color: #F5F7FA !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0px !important;
        transition: color 0.25s ease, border-color 0.25s ease, background 0.25s ease !important;
    }

    [data-testid="stVerticalBlock"]:has(.lang-btn-marker) [data-testid="stButton"] button:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }

    [data-testid="stVerticalBlock"]:has(.lang-btn-marker) [data-testid="stButton"] button:focus {
        box-shadow: none !important;
    }

    [data-testid="stColumn"]:has(.hero-btn-marker) [data-testid="stPageLink"] a {
        background: #F5F7FA !important;
        background-color: #F5F7FA !important;
        border-radius: 6px !important;
        padding: 12px 24px !important;
        justify-content: center !important;
        border: none !important;
        transition: all 0.25s ease !important;
    }
    /* Atacando a tag P interna do Streamlit para forçar a cor preta */
    [data-testid="stColumn"]:has(.hero-btn-marker) [data-testid="stPageLink"] a p {
        color: #080A0F !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin: 0 !important;
    }
    [data-testid="stColumn"]:has(.hero-btn-marker) [data-testid="stPageLink"] a:hover {
        background: linear-gradient(90deg, #8B5CF6, #06B6D4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(6, 182, 212, 0.3) !important;
    }
    [data-testid="stColumn"]:has(.hero-btn-marker) [data-testid="stPageLink"] a:hover p {
        color: #F5F7FA !important;
    }

    /* Queue patient cards — horizontal scroll with dynamic centering */
    .queue-container {
        display: flex; flex-wrap: nowrap; overflow-x: auto;
        scroll-behavior: smooth; gap: 12px;
        align-items: center; padding: 20px 0 24px 0;
        scrollbar-width: thin; scrollbar-color: #8b5cf6 #10131a;
        width: max-content;
        max-width: 100%;
        margin: 0 auto;
    }
    .queue-container::-webkit-scrollbar { height: 4px; }
    .queue-container::-webkit-scrollbar-track  { background: #10131a; }
    .queue-container::-webkit-scrollbar-thumb  { background: #8b5cf6; border-radius: 2px; }

    .patient-card {
        flex-shrink: 0; min-width: 140px;
        background-color: #151922;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 6px; padding: 16px 20px;
        position: relative; overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .patient-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255,255,255,0.14);
    }
    .patient-card::before {
        content: ''; position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
    }
    .patient-card-id   { font-size: 15px; font-weight: 600; color: #F5F7FA; margin-bottom: 4px; }
    .patient-card-prob { font-size: 13px; font-weight: 700; letter-spacing: 0.5px; }
    .patient-card-cat  { font-size: 11px; color: #8b93a7; margin-top: 4px; letter-spacing: 0.3px; }
    .queue-arrow { color: #8b93a7; font-size: 18px; align-self: center; flex-shrink: 0; }

    /* Manchester risk colors */
    .risk-red::before    { background-color: #ef4444; }
    .risk-orange::before { background-color: #f97316; }
    .risk-yellow::before { background-color: #f59e0b; }
    .risk-green::before  { background-color: #10b981; }
    .risk-blue::before   { background-color: #3b82f6; }
    .text-red    { color: #ef4444; }
    .text-orange { color: #f97316; }
    .text-yellow { color: #f59e0b; }
    .text-green  { color: #10b981; }
    .text-blue   { color: #3b82f6; }

    /* Layout Constraints (Cards, Stats, Setup, Methodology) */
    [data-testid="stHorizontalBlock"]:has(.module-card),
    [data-testid="stHorizontalBlock"]:has(.stat-pill) {
        max-width: 900px;
        margin: 0 auto;
    }

    /* Bug Global de Espacamento Superior/Inferior (96px/160px) */
    [data-testid="block-container"], 
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem !important; /* Corrige excesso superior mantendo espaco da navbar */
        padding-bottom: 2rem !important; /* Corrige excesso inferior */
    }
    footer[data-testid="stFooter"] {
        display: none !important;
    }
    [data-testid="stAppViewContainer"] > section:last-child {
        padding-bottom: 0 !important;
    }

    /* Section label */
    .section-label {
        font-size: 11px; font-weight: 700; letter-spacing: 2px;
        color: #8B5CF6; margin-bottom: 24px;
        text-transform: uppercase;
        text-align: center;
    }

    /* =========================================================
       4. BOTÃO "EXECUTAR SIMULAÇÃO" (Evitar texto quebrado)
    ========================================================= */
    [data-testid="stColumn"]:has(.setup-label) [data-testid="stButton"] button {
        width: 100% !important;
    }
    /* Forçando a tag P interna a não quebrar a linha */
    [data-testid="stColumn"]:has(.setup-label) [data-testid="stButton"] button p {
        white-space: nowrap !important;
        font-size: 14px !important;
        margin: 0 !important;
    }

    /* Methodology page width constraint */
    [data-testid="block-container"]:has(.methodology-page-marker) {
        max-width: 900px !important;
        margin: 0 auto !important;
    }

    /* Module cards (Overview) — with hover microinteraction */
    .module-card {
        background-color: #151922;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 8px; padding: 28px 32px; height: 100%;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .module-card:hover {
        transform: translateY(-4px);
        border-color: rgba(139, 92, 246, 0.40);
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
    }
    .module-number { font-size: 11px; color: #8b5cf6; font-weight: 700; letter-spacing: 1px; margin-bottom: 10px; }
    .module-title  { font-size: 17px; font-weight: 600; color: #F5F7FA; margin-bottom: 8px; }
    .module-desc   { font-size: 14px; color: #8b93a7; line-height: 1.65; }


    /* Stats pill (Overview) */
    .stat-pill {
        text-align: center; padding: 20px 12px;
        background: #10131A; border: 1px solid rgba(255,255,255,0.07);
        border-radius: 8px;
        transition: border-color 0.25s ease;
    }
    .stat-pill:hover { border-color: rgba(139, 92, 246, 0.3); }
    .stat-value { font-size: 28px; font-weight: 700; color: #8b5cf6; }
    .stat-label { font-size: 10px; color: #8b93a7; margin-top: 4px; letter-spacing: 0.7px; }

    /* Experiment setup box */
    .setup-box {
        background-color: #10131A;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 32px 40px; margin-bottom: 8px;
    }
    .setup-label {
        font-size: 11px; font-weight: 700; letter-spacing: 2px;
        color: #8b5cf6; text-transform: uppercase; margin-bottom: 24px;
    }

    /* Audit info card (replaces st.info) */
    .audit-info {
        background: #10131A; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 6px; padding: 16px 20px; margin-bottom: 16px;
        color: #8b93a7; font-size: 13px; line-height: 1.6;
    }

    /* Conclusion boxes (Methodology) */
    .conclusion-box {
        background: #10131A; border-left: 3px solid #8b5cf6;
        border-radius: 0 6px 6px 0; padding: 20px 24px; margin-bottom: 16px;
    }
    .conclusion-title {
        font-size: 14px; font-weight: 600; color: #F5F7FA; margin-bottom: 8px;
    }
    .conclusion-body { font-size: 13px; color: #8b93a7; line-height: 1.65; }

    /* Empirical highlight box */
    .highlight-box {
        background: rgba(139, 92, 246, 0.08);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 6px; padding: 20px 24px; margin: 8px 0 20px 0;
        text-align: center;
    }
    .highlight-value { font-size: 40px; font-weight: 700; color: #8b5cf6; line-height: 1; }
    .highlight-label { font-size: 13px; color: #8b93a7; margin-top: 6px; }

    /* Footer */
    .standard-footer {
        margin-top: 60px; padding: 24px 0;
        border-top: 1px solid rgba(255,255,255,0.07);
        color: #8b93a7; font-family: 'Inter', sans-serif;
        display: flex; flex-direction: column;
        align-items: center; background-color: transparent;
    }
    .standard-footer .footer-text { margin-bottom: 12px; font-size: 13px; text-align: center; }
    .standard-footer .footer-links { display: flex; gap: 28px; flex-wrap: wrap; justify-content: center; }
    .standard-footer a {
        color: #8b5cf6; text-decoration: none; font-size: 13px;
        font-weight: 500; display: flex; align-items: center; gap: 6px;
    }
    .standard-footer a:hover { color: #06b6d4; }

    /* ---- Responsive breakpoints ---- */
    @media (max-width: 900px) {
        .module-card { padding: 22px 24px; }
        .setup-box   { padding: 24px; }
    }
    @media (max-width: 600px) {
        .module-card { padding: 18px 16px; }
        .module-title { font-size: 15px; }
        .module-desc  { font-size: 13px; }
        .stat-value   { font-size: 22px; }
        .setup-box    { padding: 18px 16px; }
        .patient-card { min-width: 120px; padding: 12px 14px; }
        .highlight-value { font-size: 32px; }
    }
</style>
"""



def injetar_css_global() -> None:
    """Injeta o CSS premium global (Inter, navbar, cards, queue) na pagina atual."""
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


def renderizar_navbar(t: Dict[str, Any], lang: str) -> None:
    """Renderiza a navbar premium do TRIAGE.AI."""

    if "lang" not in st.session_state:
        st.session_state["lang"] = "pt"

    col_logo, col_nav, col_lang = st.columns(
        [1, 2, 1],
        vertical_alignment="center",
    )

    with col_logo:
        st.markdown(
            '<div class="logo-container">&#9672; TRIAGE.AI</div>',
            unsafe_allow_html=True,
        )

    with col_nav:
        # Marcador para isolar a regra CSS da capsula
        st.markdown('<span class="nav-capsule-marker"></span>', unsafe_allow_html=True)
        nav1, nav2, nav3 = st.columns(3, gap="small")

        with nav1:
            st.page_link(
                "main.py",
                label=t.get("nav_overview", "01 OVERVIEW"),
                use_container_width=True,
            )

        with nav2:
            st.page_link(
                "pages/2_Simulation.py",
                label=t.get("nav_simulation", "02 SIMULATION"),
                use_container_width=True,
            )

        with nav3:
            st.page_link(
                "pages/3_Methodology.py",
                label=t.get("nav_methodology", "03 METHODOLOGY"),
                use_container_width=True,
            )

    with col_lang:
        # Marcador para isolar a regra CSS do botao de idioma
        st.markdown('<span class="lang-btn-marker"></span>', unsafe_allow_html=True)
        idioma_alvo = "EN" if lang == "pt" else "PT"

        if st.button(
            idioma_alvo,
            key="navbar_language",
            help="Change language" if lang == "pt" else "Mudar idioma",
        ):
            st.session_state["lang"] = idioma_alvo.lower()
            st.rerun()


# ---------------------------------------------------------------------------
# Protocolo de Manchester — Paleta de Cores Oficial
# Mapeamento de probabilidade_alta [0.0, 1.0] para 5 categorias clinicas.
# ---------------------------------------------------------------------------

PALETA_MANCHESTER: Dict[str, str] = {
    "Nao Urgente":   "#3b82f6",
    "Pouco Urgente": "#10b981",
    "Urgente":       "#f59e0b",
    "Muito Urgente": "#f97316",
    "Emergencia":    "#ef4444",
}

_LIMIARES_MANCHESTER = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
_CATEGORIAS_MANCHESTER = list(PALETA_MANCHESTER.keys())

_MANCHESTER_CSS: Dict[str, Tuple[str, str]] = {
    "Nao Urgente":   ("risk-blue",   "text-blue"),
    "Pouco Urgente": ("risk-green",  "text-green"),
    "Urgente":       ("risk-yellow", "text-yellow"),
    "Muito Urgente": ("risk-orange", "text-orange"),
    "Emergencia":    ("risk-red",    "text-red"),
}

_MANCHESTER_I18N_KEY: Dict[str, str] = {
    "Nao Urgente":   "manch_nao_urgente",
    "Pouco Urgente": "manch_pouco_urgente",
    "Urgente":       "manch_urgente",
    "Muito Urgente": "manch_muito_urgente",
    "Emergencia":    "manch_emergencia",
}


def classificar_manchester(probabilidade_alta: float) -> str:
    """Classifica um paciente nas categorias do Protocolo de Manchester.

    Args:
        probabilidade_alta: Probabilidade de gravidade alta em [0.0, 1.0].

    Returns:
        Nome interno da categoria Manchester (chave de PALETA_MANCHESTER).
    """
    prob = max(0.0, min(1.0, probabilidade_alta))
    for i, limite_superior in enumerate(_LIMIARES_MANCHESTER[1:]):
        if prob < limite_superior:
            return _CATEGORIAS_MANCHESTER[i]
    return _CATEGORIAS_MANCHESTER[-1]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def formatar_numero_br(valor: float) -> str:
    """Formata um numero float para o padrao brasileiro (1.234,56)."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _get_t_default() -> Dict[str, Any]:
    from src.ui.i18n import get_t
    return get_t(st.session_state.get("lang", "pt"))


# ---------------------------------------------------------------------------
# Patient Queue Cards
# ---------------------------------------------------------------------------


def renderizar_cards_pacientes(
    lista_pacientes: List[Paciente],
    ordem: List[int],
    t: Dict[str, Any],
) -> None:
    """Renderiza a fila otimizada como cards horizontais com scroll suave.

    Cada card exibe ID do paciente, nivel de risco percentual e categoria
    do Protocolo de Manchester com borda colorida correspondente.

    Args:
        lista_pacientes: Lista completa de pacientes da simulacao.
        ordem: Sequencia de IDs na ordem otimizada pelo A*.
        t: Dicionario de traducoes para a lingua corrente.
    """
    pacientes_por_id = {p.id_paciente: p for p in lista_pacientes}

    def _risk_label(prob: float) -> str:
        if prob >= 0.60:
            return str(t["card_risk_high"])
        if prob >= 0.40:
            return str(t["card_risk_med"])
        return str(t["card_risk_low"])

    cards_html = '<div class="queue-container">'

    for idx, pid in enumerate(ordem):
        p = pacientes_por_id.get(pid)
        if p is None:
            continue

        categoria = classificar_manchester(p.probabilidade_alta)
        css_border, css_text = _MANCHESTER_CSS.get(categoria, ("risk-blue", "text-blue"))
        i18n_key = _MANCHESTER_I18N_KEY.get(categoria, "manch_nao_urgente")
        display_cat = t.get(i18n_key, categoria)
        risk_lbl = _risk_label(p.probabilidade_alta)
        prob_pct = int(p.probabilidade_alta * 100)

        cards_html += f"""
        <div class="patient-card {css_border}">
            <div class="patient-card-id">{t["card_prefix"]}-{pid:02d}</div>
            <div class="patient-card-prob {css_text}">{risk_lbl} {prob_pct}%</div>
            <div class="patient-card-cat">{display_cat}</div>
        </div>"""

        if idx < len(ordem) - 1:
            cards_html += '<div class="queue-arrow">&rarr;</div>'

    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# KPIs de Business Intelligence
# ---------------------------------------------------------------------------


def renderizar_kpis_bi(
    resultado: ResultadoSimulacao,
    t: Dict[str, Any] | None = None,
) -> None:
    """Renderiza o painel de KPIs de Business Intelligence."""
    if t is None:
        t = _get_t_default()

    col1, col2, col3, col4 = st.columns(4)
    tempo_ms = resultado.tempo_execucao_segundos * 1000

    with col1:
        st.metric(t["kpi_exec_time"], f"{tempo_ms:.0f} ms", help=t["kpi_exec_help"])
    with col2:
        st.metric(
            t["kpi_nodes"],
            f"{resultado.nos_explorados_a_star:,}".replace(",", "."),
            help=t["kpi_nodes_help"],
        )

    espera = resultado.tempo_medio_espera_por_estrategia
    espera_fifo = espera.get("fifo", 0.0)
    espera_a_star = espera.get("a_star", 0.0)
    delta_espera = espera_a_star - espera_fifo

    with col3:
        st.metric(t["kpi_wait_fifo"], f"{espera_fifo:.1f} min", help=t["kpi_wait_fifo_help"])
    with col4:
        st.metric(
            t["kpi_wait_astar"],
            f"{espera_a_star:.1f} min",
            delta=f"{delta_espera:+.1f} min vs FIFO",
            delta_color="inverse",
            help=t["kpi_wait_astar_help"],
        )


# ---------------------------------------------------------------------------
# Graficos
# ---------------------------------------------------------------------------


def renderizar_metricas(
    resultado: ResultadoSimulacao,
    t: Dict[str, Any] | None = None,
) -> None:
    """Renderiza os cards de risco comparativos."""
    if t is None:
        t = _get_t_default()

    delta = resultado.risco_a_star - resultado.risco_gulosa
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t["metric_fifo"], formatar_numero_br(resultado.risco_fifo))
    with col2:
        st.metric(t["metric_greedy"], formatar_numero_br(resultado.risco_gulosa))
    with col3:
        st.metric(
            t["metric_astar"],
            formatar_numero_br(resultado.risco_a_star),
            delta=f"{delta:+.2f} {t['metric_delta_label']}",
            delta_color="inverse",
        )


def renderizar_grafico_perfil_clinico(
    lista_pacientes: List[Paciente],
    t: Dict[str, Any] | None = None,
    key: str | None = None,
) -> None:
    """Renderiza o histograma de distribuicao pelo Protocolo de Manchester.

    Args:
        lista_pacientes: Pacientes da simulacao.
        t: Dicionario de traducoes.
        key: Chave unica para evitar StreamlitDuplicateElementId.
    """
    if t is None:
        t = _get_t_default()

    registros = [
        {"Categoria": classificar_manchester(p.probabilidade_alta)}
        for p in lista_pacientes
    ]
    df = pd.DataFrame(registros)
    df["Categoria"] = pd.Categorical(
        df["Categoria"], categories=_CATEGORIAS_MANCHESTER, ordered=True
    )

    fig = px.histogram(
        df, x="Categoria", color="Categoria",
        color_discrete_map=PALETA_MANCHESTER, text_auto=True,
        category_orders={"Categoria": _CATEGORIAS_MANCHESTER},
    )
    fig.update_layout(
        title=dict(text=t["chart_profile_title"], font=dict(size=13)),
        xaxis_title=None, yaxis_title=t["chart_y_patients"],
        showlegend=False,
        margin=dict(t=40, b=0, l=0, r=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def renderizar_grafico_risco_acumulado(
    resultado: ResultadoSimulacao,
    t: Dict[str, Any] | None = None,
    key: str | None = None,
) -> None:
    """Renderiza o grafico de barras comparativo do risco acumulado global.

    Args:
        resultado: Resultado completo da simulacao.
        t: Dicionario de traducoes.
        key: Chave unica para evitar StreamlitDuplicateElementId.
    """
    if t is None:
        t = _get_t_default()

    labels = [t["chart_fifo"], t["chart_greedy"], t["chart_astar"]]
    values = [resultado.risco_fifo, resultado.risco_gulosa, resultado.risco_a_star]
    cores = ["#636EFA", "#EF553B", "#00CC96"]

    fig = go.Figure(
        go.Bar(
            x=values, y=labels, orientation="h", marker_color=cores,
            text=[f"{v:,.2f}" for v in values], textposition="outside",
        )
    )

    positivos = [v for v in values if v > 0]
    min_r = min(positivos) if positivos else 0.0
    max_r = max(values) if values else 1.0
    margem = (max_r - min_r) * 0.5 if max_r != min_r else max_r * 0.1

    fig.update_layout(
        title=dict(text=t["chart_risk_title"], font=dict(size=13)),
        xaxis=dict(range=[max(0, min_r - margem), max_r + margem], title=t["chart_x_risk"]),
        yaxis_title=None, showlegend=False,
        margin=dict(t=40, b=0, l=0, r=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def renderizar_grafico_risco_streaming(
    risco_fifo: float,
    risco_gulosa: float,
    risco_a_star_parcial: float,
    lote_atual: int,
    total_lotes: int,
    t: Dict[str, Any] | None = None,
) -> go.Figure:
    """Constroi o grafico de risco para atualizacao em streaming (retorna Figure)."""
    if t is None:
        t = _get_t_default()

    label_astar = (
        f"{t['chart_astar']} — {lote_atual}/{total_lotes}"
        if lote_atual < total_lotes
        else t["chart_astar"]
    )

    labels = [t["chart_fifo"], t["chart_greedy"], label_astar]
    values = [risco_fifo, risco_gulosa, risco_a_star_parcial]
    cores = ["#636EFA", "#EF553B", "#00CC96"]

    fig = go.Figure(
        go.Bar(
            x=values, y=labels, orientation="h", marker_color=cores,
            text=[f"{v:,.2f}" for v in values], textposition="outside",
        )
    )

    positivos = [v for v in values if v > 0]
    min_r = min(positivos) if positivos else 0.0
    max_r = max(values) if values else 1.0
    margem = (max_r - min_r) * 0.5 if max_r != min_r else max_r * 0.1

    fig.update_layout(
        xaxis=dict(range=[max(0, min_r - margem), max_r + margem], title=t["chart_x_risk"]),
        yaxis_title=None, showlegend=False,
        margin=dict(t=20, b=0, l=0, r=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ---------------------------------------------------------------------------
# Abas compostas
# ---------------------------------------------------------------------------


def renderizar_aba_executiva(
    resultado: ResultadoSimulacao,
    t: Dict[str, Any] | None = None,
    key_prefix: str = "exec",
) -> None:
    """Renderiza a aba Visao Executiva: KPIs, metricas e graficos.

    Args:
        resultado: Resultado completo da simulacao.
        t: Dicionario de traducoes.
        key_prefix: Prefixo para chaves unicas dos graficos Plotly.
    """
    if t is None:
        t = _get_t_default()

    renderizar_kpis_bi(resultado, t)
    st.markdown("---")
    renderizar_metricas(resultado, t)
    st.markdown("---")

    col_esq, col_dir = st.columns(2)
    with col_esq:
        renderizar_grafico_perfil_clinico(
            resultado.lista_pacientes, t, key=f"{key_prefix}_perfil"
        )
    with col_dir:
        renderizar_grafico_risco_acumulado(
            resultado, t, key=f"{key_prefix}_risco"
        )


def renderizar_aba_auditoria(
    resultado: ResultadoSimulacao,
    t: Dict[str, Any] | None = None,
) -> None:
    """Renderiza a aba Auditoria de Fila com tabelas e exportacao CSV."""
    if t is None:
        t = _get_t_default()

    st.markdown(
        f'<div class="audit-info">{t["sim_audit_info"]}</div>',
        unsafe_allow_html=True,
    )

    df_astar = gerar_dataframe_auditoria(resultado.lista_pacientes, resultado.ordem_a_star)
    st.download_button(
        label=t["sim_download_btn"],
        data=df_astar.to_csv(index=False).encode("utf-8"),
        file_name="auditoria_fila_a_star.csv",
        mime="text/csv",
    )

    st.markdown(f"#### {t['sim_audit_astar']}")
    st.dataframe(df_astar, use_container_width=True)

    st.markdown(f"#### {t['sim_audit_greedy']}")
    st.dataframe(
        gerar_dataframe_auditoria(resultado.lista_pacientes, resultado.ordem_gulosa),
        use_container_width=True,
    )

    st.markdown(f"#### {t['sim_audit_fifo']}")
    st.dataframe(
        gerar_dataframe_auditoria(resultado.lista_pacientes, resultado.ordem_fifo),
        use_container_width=True,
    )


def renderizar_resultados(
    resultado: ResultadoSimulacao,
    t: Dict[str, Any] | None = None,
    key_prefix: str = "final",
) -> None:
    """Renderiza a secao completa de resultados com abas.

    Args:
        resultado: Resultado completo da simulacao.
        t: Dicionario de traducoes.
        key_prefix: Prefixo para chaves unicas dos graficos Plotly.
    """
    if t is None:
        t = _get_t_default()

    aba_exec, aba_audit = st.tabs([t["sim_report_header"], t["sim_audit_header"]])
    with aba_exec:
        renderizar_aba_executiva(resultado, t, key_prefix=key_prefix)
    with aba_audit:
        renderizar_aba_auditoria(resultado, t)


# ---------------------------------------------------------------------------
# Rodape
# ---------------------------------------------------------------------------


def renderizar_rodape(t: Dict[str, Any] | None = None) -> None:
    """Renderiza o rodape HTML com links do autor."""
    if t is None:
        t = _get_t_default()

    st.markdown(
        f"""
        <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <div class="standard-footer">
            <div class="footer-text"><strong>&copy; 2026 {t["footer_by"]}</strong></div>
            <div class="footer-links">
                <a href="https://github.com/fhugomp" target="_blank">
                    <i class="fab fa-github"></i> {t["footer_github"]}
                </a>
                <a href="https://linkedin.com/in/fhugomp" target="_blank">
                    <i class="fab fa-linkedin"></i> {t["footer_linkedin"]}
                </a>
                <a href="https://fhugomp.github.io" target="_blank">
                    <i class="fas fa-globe"></i> {t["footer_portfolio"]}
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
