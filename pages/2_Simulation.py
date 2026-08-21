"""
Pagina: 2_Simulation
Dashboard de execucao com Experiment Setup centralizado, streaming frame-a-frame
e visualizacao da fila otimizada em cards do Protocolo de Manchester.
"""

import time
from typing import cast, Literal

import streamlit as st

import src.config as config
from src.data.generator import GeradorPacientesSinteticos
from src.models.bayesian_net import SistemaTriagemBayesiana
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem
from src.simulation.runner import (
    ResultadoSimulacao,
    SnapshotSimulacao,
    _calcular_tempo_medio_espera,
    executar_simulacao_streaming,
)
from src.ui.components import (
    injetar_css_global,
    renderizar_cards_pacientes,
    renderizar_grafico_perfil_clinico,
    renderizar_grafico_risco_streaming,
    renderizar_navbar,
    renderizar_resultados,
    renderizar_rodape,
)
from src.ui.i18n import get_t

st.set_page_config(
    page_title="TRIAGE.AI — Simulation",
    layout="wide",
    initial_sidebar_state="collapsed",
)

injetar_css_global()

if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"
lang = st.session_state["lang"]
t = get_t(lang)

renderizar_navbar(t, lang)

# ---------------------------------------------------------------------------
# Cabecalho da pagina
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div style="padding: 8px 0 20px 0;">
        <h1 style="font-size:36px; font-weight:700; letter-spacing:-1px;
                   color:#F5F7FA; margin:0 0 6px 0; font-family:'Inter',sans-serif;">
            {t["sim_title"]}
        </h1>
        <p style="color:#8b93a7; font-size:15px; font-weight:300; margin:0;
                  font-family:'Inter',sans-serif;">
            {t["sim_subtitle"]}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 32px 0;">',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Inicializacao do sistema (cached)
# ---------------------------------------------------------------------------


@st.cache_resource
def inicializar_sistema() -> (
    tuple[SistemaTriagemBayesiana, OtimizadorTriagemAStar, BaselinesTriagem]
):
    """Inicializa e armazena em cache os componentes do sistema."""
    rbn = SistemaTriagemBayesiana()
    a_star = OtimizadorTriagemAStar(
        tempo_atendimento_minutos=config.TEMPO_ATENDIMENTO_MINUTOS
    )
    baselines = BaselinesTriagem(
        tempo_atendimento_minutos=config.TEMPO_ATENDIMENTO_MINUTOS
    )
    return rbn, a_star, baselines


rbn, a_star, baselines = inicializar_sistema()
gerador = GeradorPacientesSinteticos(seed=None)

# ---------------------------------------------------------------------------
# Experiment Setup — controles centralizados
# ---------------------------------------------------------------------------

_, col_setup, _ = st.columns([1, 3, 1])

with col_setup:
    st.markdown(
        f'<div class="setup-box">'
        f'<div class="setup-label">{t["sim_setup_header"]}</div>',
        unsafe_allow_html=True,
    )

    num_pacientes = st.slider(
        t["sim_num_patients_label"],
        min_value=config.SLIDER_MIN_PACIENTES,
        max_value=config.SLIDER_MAX_PACIENTES,
        value=config.SLIDER_DEFAULT_PACIENTES,
        step=1,
    )

    col_fn, col_mode = st.columns(2)
    with col_fn:
        tipo_funcao_sel = st.radio(
            t["sim_risk_fn_label"],
            options=[t["sim_risk_linear"], t["sim_risk_exp"]],
        )
    with col_mode:
        modo_a_star = st.radio(
            t["sim_mode_label"],
            options=[t["sim_mode_global"], t["sim_mode_part"]],
        )

    usar_janela = modo_a_star == t["sim_mode_part"]
    tipo_funcao = cast(
        Literal["linear", "exponencial"],
        "linear" if tipo_funcao_sel == t["sim_risk_linear"] else "exponencial",
    )
    estrategia_part: Literal["fifo", "risco_inicial"] = "risco_inicial"

    bloquear_execucao = False
    if not usar_janela and num_pacientes > 8:
        st.error(t["sim_block_error"])
        bloquear_execucao = True

    executar = st.button(
        t["sim_btn"],
        type="primary",
        disabled=bloquear_execucao,
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Execucao com Streaming
# ---------------------------------------------------------------------------

if executar:
    st.markdown(
        '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:24px 0;">',
        unsafe_allow_html=True,
    )

    progresso_bar = st.progress(0, text=t["sim_initializing"])
    status_placeholder = st.empty()

    st.markdown(
        f'<div class="section-label" style="margin-top:24px;">'
        f'{t["sim_queue_header"]}</div>',
        unsafe_allow_html=True,
    )
    container_cards = st.empty()

    col_stream_esq, col_stream_dir = st.columns(2)
    with col_stream_esq:
        container_perfil = st.empty()
    with col_stream_dir:
        container_risco = st.empty()

    # --- Streaming frame-a-frame ---
    inicio_wall = time.perf_counter()
    ultimo_snapshot: SnapshotSimulacao | None = None

    for snapshot in executar_simulacao_streaming(
        num_pacientes=num_pacientes,
        tipo_funcao=tipo_funcao,
        estrategia_particionamento=estrategia_part,
        usar_janela=usar_janela,
        gerador=gerador,
        rbn=rbn,
        a_star=a_star,
        baselines=baselines,
    ):
        ultimo_snapshot = snapshot

        progresso = snapshot.lote_atual / snapshot.total_lotes
        progresso_bar.progress(
            progresso,
            text=t["sim_progress_text"].format(
                current=snapshot.lote_atual,
                total=snapshot.total_lotes,
            ),
        )
        status_placeholder.caption(
            t["sim_nodes_label"].format(
                n=f"{snapshot.nos_explorados_ate_agora:,}".replace(",", ".")
            )
        )

        # Perfil clinico: renderiza somente no primeiro frame (pacientes fixos)
        if snapshot.lote_atual == 1:
            with container_perfil:
                renderizar_grafico_perfil_clinico(
                    snapshot.lista_pacientes, t, key="stream_perfil"
                )

        # Cards: atualiza a cada lote
        with container_cards:
            renderizar_cards_pacientes(
                snapshot.lista_pacientes, snapshot.ordem_a_star_parcial, t
            )

        # Grafico de risco: atualiza a cada lote
        fig_risco = renderizar_grafico_risco_streaming(
            risco_fifo=snapshot.risco_fifo,
            risco_gulosa=snapshot.risco_gulosa,
            risco_a_star_parcial=snapshot.risco_a_star_parcial,
            lote_atual=snapshot.lote_atual,
            total_lotes=snapshot.total_lotes,
            t=t,
        )
        container_risco.plotly_chart(fig_risco, use_container_width=True)

        if not snapshot.concluido:
            time.sleep(0.4)

    fim_wall = time.perf_counter()
    progresso_bar.progress(1.0, text=t["sim_completed"])
    status_placeholder.empty()

    # --- Resultado final consolidado a partir do ultimo snapshot ---
    if ultimo_snapshot is not None:
        tempo_medio = {
            "fifo": _calcular_tempo_medio_espera(
                ultimo_snapshot.lista_pacientes,
                ultimo_snapshot.ordem_fifo,
                a_star.tempo_atendimento,
            ),
            "gulosa": _calcular_tempo_medio_espera(
                ultimo_snapshot.lista_pacientes,
                ultimo_snapshot.ordem_gulosa,
                a_star.tempo_atendimento,
            ),
            "a_star": _calcular_tempo_medio_espera(
                ultimo_snapshot.lista_pacientes,
                ultimo_snapshot.ordem_a_star_parcial,
                a_star.tempo_atendimento,
            ),
        }

        resultado_final = ResultadoSimulacao(
            lista_pacientes=ultimo_snapshot.lista_pacientes,
            ordem_fifo=ultimo_snapshot.ordem_fifo,
            risco_fifo=ultimo_snapshot.risco_fifo,
            ordem_gulosa=ultimo_snapshot.ordem_gulosa,
            risco_gulosa=ultimo_snapshot.risco_gulosa,
            ordem_a_star=ultimo_snapshot.ordem_a_star_parcial,
            risco_a_star=ultimo_snapshot.risco_a_star_parcial,
            tempo_execucao_segundos=fim_wall - inicio_wall,
            nos_explorados_a_star=ultimo_snapshot.nos_explorados_ate_agora,
            tempo_medio_espera_por_estrategia=tempo_medio,
        )

        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:24px 0;">',
            unsafe_allow_html=True,
        )
        # key_prefix "final" differs from "stream_*" keys above → no duplicate IDs
        renderizar_resultados(resultado_final, t, key_prefix="final")

renderizar_rodape(t)
