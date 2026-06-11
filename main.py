import streamlit as st
from typing import cast, List, Dict, Any, Tuple, Literal
from src import config
from src.data.generator import GeradorPacientesSinteticos
from src.models.bayesian_net import SistemaTriagemBayesiana
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem

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
def inicializar_sistema() -> (
    Tuple[
        GeradorPacientesSinteticos,
        SistemaTriagemBayesiana,
        OtimizadorTriagemAStar,
        BaselinesTriagem,
    ]
):
    gerador = GeradorPacientesSinteticos(seed=config.SEED_DETERMINISTICA)
    rbn = SistemaTriagemBayesiana()
    a_star = OtimizadorTriagemAStar(
        tempo_atendimento_minutos=config.TEMPO_ATENDIMENTO_MINUTOS
    )
    baselines = BaselinesTriagem(
        tempo_atendimento_minutos=config.TEMPO_ATENDIMENTO_MINUTOS
    )
    return gerador, rbn, a_star, baselines


gerador, rbn, a_star, baselines = inicializar_sistema()

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
    Literal["linear", "exponencial"], str(tipo_funcao_selecionada).lower()
)

st.sidebar.markdown("### Motor Otimizador (Algoritmo A*)")
modo_a_star = st.sidebar.radio(
    "Modo de Execução:",
    options=["A* Global (Ótimo Matemático)", "A* Particionado (Sliding Window)"],
    help="Global: Explora todo o espaço de estados simultaneamente. Particionado: Utiliza lotes para mitigar a explosão combinatória.",
)
usar_janela = modo_a_star == "A* Particionado (Sliding Window)"

# Se o usuário escolheu particionado, ele pode escolher a heurística do lote
estrategia_part = "fifo"
if usar_janela:
    estrategia_selecionada = st.sidebar.selectbox(
        "Heurística de Particionamento dos Lotes:",
        options=["Aproximação FIFO", "Risco Inicial (Mitiga Miopia)"],
    )
    map_estrategia: Dict[str, Literal["fifo", "risco_inicial"]] = {
        "Aproximação FIFO": "fifo",
        "Risco Inicial (Mitiga Miopia)": "risco_inicial",
    }
    estrategia_part = map_estrategia[str(estrategia_selecionada)]

    if estrategia_part == "fifo":
        st.sidebar.info(
            "Modo FIFO Ativo: O algoritmo prioriza o tempo de espera para formar os blocos, gerando 'miopia local' em populações grandes."
        )
    else:
        st.sidebar.success(
            "Risco Inicial Ativo: O algoritmo prioriza a gravidade na formação dos blocos, mitigando a miopia da janela."
        )

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
        # --- PASSO A: Geração de Dados e Rede Bayesiana ---
        df_pacientes = gerador.gerar_pacientes(num_pacientes)

        probabilidades_alta = []
        for _, row in df_pacientes.iterrows():
            evidencias = {
                "IdadeAvancada": str(row["IdadeAvancada"]),
                "DoencaCronica": str(row["DoencaCronica"]),
                "SaturacaoO2": str(row["SaturacaoO2"]),
                "FrequenciaCardiaca": str(row["FrequenciaCardiaca"]),
                "NivelDor": str(row["NivelDor"]),
                "Febre": str(row["Febre"]),
            }

            probs = rbn.calcular_probabilidade_gravidade(evidencias)
            probabilidades_alta.append(probs["alta"] if probs else 0.0)

        df_pacientes["Probabilidade_Alta"] = probabilidades_alta
        lista_pacientes = cast(List[Dict[str, Any]], df_pacientes.to_dict("records"))

        # --- PASSO B: Execução Simulânea das Estratégias ---
        ordem_fifo, risco_fifo = baselines.simular_fifo(
            lista_pacientes.copy(), tipo_funcao
        )
        ordem_gulosa, risco_gulosa = baselines.simular_gulosa(
            lista_pacientes.copy(), tipo_funcao
        )

        ordem_a_star, risco_a_star = a_star.otimizar_fila(
            lista_pacientes.copy(),
            tipo_funcao=tipo_funcao,
            estrategia_particionamento=cast(
                Literal["fifo", "risco_inicial"], estrategia_part
            ),
            usar_janela=usar_janela,
        )

        # --- PASSO C: Renderização Analítica dos Resultados ---
        st.markdown("#### Análise Comparativa de Risco Acumulado")

        if tipo_funcao == "linear":
            st.markdown(
                "> *Nota: O Risco Acumulado é modelado pela função linear $f(t) = P(Alta) \\times t$, onde menores valores indicam maior preservação da integridade clínica global.*"
            )
        else:
            st.markdown(
                "> *Nota: O Risco Acumulado é modelado pela função exponencial $f(t) = P(Alta) \\times e^{t/\\tau}$, simulando cenários não lineares de deterioração acelerada.*"
            )

        col1, col2, col3 = st.columns(3)

        col1.metric("1. Estratégia FIFO (Controle)", f"{risco_fifo:.2f}")
        col2.metric("2. Estratégia Gulosa (Greedy)", f"{risco_gulosa:.2f}")

        delta_val = risco_fifo - risco_a_star
        col3.metric(
            "3. Otimização por Algoritmo A-Star",
            f"{risco_a_star:.2f}",
            delta=f"Redução Absoluta: {delta_val:.2f}",
            delta_color="normal",
        )

        st.divider()

        st.markdown("#### Distribuição de Filas e Ordem de Atendimento")
        c1, c2, c3 = st.columns(3)

        col_config = {
            "ID_Paciente": st.column_config.NumberColumn("ID", format="%d"),
            "TempoEspera_Inicial_Minutos": st.column_config.NumberColumn(
                "Tempo Fila (min)", format="%d"
            ),
            "Probabilidade_Alta": st.column_config.NumberColumn(
                "P(Alta)", format="%.4f"
            ),
            "DoencaCronica": st.column_config.TextColumn("Doença Crônica"),
        }

        with c1:
            st.markdown("**Estratégia: FIFO**")
            df_f = df_pacientes.set_index("ID_Paciente").loc[ordem_fifo].reset_index()
            st.dataframe(
                df_f[
                    [
                        "ID_Paciente",
                        "TempoEspera_Inicial_Minutos",
                        "Probabilidade_Alta",
                        "DoencaCronica",
                    ]
                ],
                use_container_width=True,
                column_config=col_config,
            )

        with c2:
            st.markdown("**Estratégia: Gulosa**")
            df_g = df_pacientes.set_index("ID_Paciente").loc[ordem_gulosa].reset_index()
            st.dataframe(
                df_g[
                    [
                        "ID_Paciente",
                        "TempoEspera_Inicial_Minutos",
                        "Probabilidade_Alta",
                        "DoencaCronica",
                    ]
                ],
                use_container_width=True,
                column_config=col_config,
            )

        with c3:
            st.markdown("**Estratégia: A-Star**")
            df_a = df_pacientes.set_index("ID_Paciente").loc[ordem_a_star].reset_index()
            st.dataframe(
                df_a[
                    [
                        "ID_Paciente",
                        "TempoEspera_Inicial_Minutos",
                        "Probabilidade_Alta",
                        "DoencaCronica",
                    ]
                ],
                use_container_width=True,
                column_config=col_config,
            )

else:
    st.info(
        "Aguardando inicialização. Ajuste os parâmetros na barra lateral e inicie a simulação para gerar os relatórios analíticos."
    )
