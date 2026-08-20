import streamlit as st
from typing import cast, Literal

import src.config as config
from src.data.generator import GeradorPacientesSinteticos
from src.models.bayesian_net import SistemaTriagemBayesiana
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem
from src.simulation.runner import executar_simulacao
from src.ui.components import renderizar_resultados, renderizar_rodape

st.set_page_config(
    page_title="Simulador de Triagem - IA",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Sistema Inteligente de Triagem Hospitalar")
st.markdown("### Otimização de Filas Baseada em Redes Bayesianas e Algoritmo A*")
st.markdown("---")

with st.expander("Sobre a Metodologia e Modelagem", expanded=False):
    st.markdown(
        """
    **Resumo:** Este simulador apresenta uma modelagem preditiva e prescritiva para o fluxo de atendimento em prontos-socorros. 
    O sistema soluciona o problema da superlotação através de dois módulos acoplados:
    1. **Inferência de Risco (Rede Bayesiana):** Estima a probabilidade de um paciente possuir gravidade clínica *Alta* dadas as evidências parciais (sintomas e sinais vitais).
    2. **Otimização Combinatória (Algoritmo A-Star):** Minimiza o risco acumulado global da fila, utilizando uma função de custo baseada na probabilidade de deterioração e no tempo de espera latente.
    """
    )


@st.cache_resource
def inicializar_sistema():
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

# Barra Lateral (Painel de Controle)
st.sidebar.markdown("### Configurações da Simulação")
num_pacientes = st.sidebar.slider(
    "Tamanho da Amostra (Pacientes)",
    min_value=config.SLIDER_MIN_PACIENTES,
    max_value=config.SLIDER_MAX_PACIENTES,
    value=config.SLIDER_DEFAULT_PACIENTES,
    step=1,
)

st.sidebar.markdown("### Modelo de Deterioração Clínica")
tipo_funcao_selecionada = st.sidebar.radio(
    "Selecione a Função de Risco:",
    options=["Linear", "Exponencial"],
    help="Linear: Risco cresce proporcionalmente ao tempo. Exponencial: Simula quadros críticos que escalam rapidamente.",
)

tipo_funcao = cast(
    Literal["linear", "exponencial"], tipo_funcao_selecionada.lower()
)

st.sidebar.markdown("### Motor Otimizador (Algoritmo A*)")
modo_a_star = st.sidebar.radio(
    "Modo de Execução:",
    options=["A* Global (Ótimo Matemático)", "A* Particionado (Sliding Window)"],
    help="Global: Explora todo o espaço de estados simultaneamente. Particionado: Utiliza lotes para mitigar a explosão combinatória.",
)
usar_janela = modo_a_star == "A* Particionado (Sliding Window)"

# Se o usuário escolheu particionado, ele pode escolher a heurística do lote
estrategia_part: Literal["fifo", "risco_inicial"] = "risco_inicial"

# Disjuntor de Segurança para Explosão Combinatória
bloquear_execucao = False
if not usar_janela and num_pacientes > 8:
    st.sidebar.error(
        "🚨 Ação Bloqueada: O A* Global explora O(N!) possibilidades. Para N > 8, o processador travaria. Reduza a amostra para 8 pacientes ou altere o modo para A* Particionado."
    )
    bloquear_execucao = True

if st.sidebar.button(
    "Executar Simulação de Cenário", type="primary", disabled=bloquear_execucao
):
    with st.spinner(
        "Processando Inferência Probabilística e Otimização do Espaço de Estados..."
    ):
        resultado = executar_simulacao(
            num_pacientes=num_pacientes,
            tipo_funcao=tipo_funcao,
            estrategia_particionamento=estrategia_part,
            usar_janela=usar_janela,
            gerador=gerador,
            rbn=rbn,
            a_star=a_star,
            baselines=baselines,
        )

        renderizar_resultados(resultado)

renderizar_rodape()
