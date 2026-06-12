import streamlit as st
import plotly.express as px
from typing import cast, Literal, List, Dict, Any, Tuple

import src.config as config
from src.data.generator import GeradorPacientesSinteticos
from src.models.bayesian_net import SistemaTriagemBayesiana
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem
from src.utils import (
    preparar_dados_grafico,
    gerar_dataframe_auditoria,
    preparar_dados_perfil_clinico,
)

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
        st.markdown("---")
        st.header("📊 Análise de Desempenho do Escalonamento")

        aba_executiva, aba_auditoria = st.tabs(
            [
                "Visão Executiva (Métricas e Gráficos)",
                "Auditoria de Fila (Dados Brutos)",
            ]
        )

        with aba_executiva:
            delta_matematico = risco_a_star - risco_gulosa

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Aproximação FIFO",
                    value=f"{risco_fifo:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                )
            with col2:
                st.metric(
                    label="Heurística Gulosa",
                    value=f"{risco_gulosa:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                )
            with col3:
                st.metric(
                    label="Busca A* (Otimizador)",
                    value=f"{risco_a_star:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                    delta=f"{delta_matematico:+.2f} vs Gulosa",
                    delta_color="inverse",
                )

            st.markdown("---")

            # Divisão espacial para aumento da densidade informacional
            grafico_esq, grafico_dir = st.columns(2)

            with grafico_esq:
                st.markdown("### Perfil Clínico da Fila (Input)")
                df_perfil = preparar_dados_perfil_clinico(lista_pacientes)

                fig_perfil = px.histogram(
                    df_perfil,
                    x="Categoria de Risco",
                    color="Categoria de Risco",
                    color_discrete_map={
                        "Baixo Risco": "#636EFA",
                        "Risco Moderado": "#FFA15A",
                        "Alto Risco": "#EF553B",
                    },
                    text_auto=True,
                )
                fig_perfil.update_layout(
                    xaxis_title=None,
                    yaxis_title="Volume de Pacientes",
                    showlegend=False,
                    margin=dict(t=20, b=0, l=0, r=0),
                )
                st.plotly_chart(fig_perfil, use_container_width=True)

            with grafico_dir:
                st.markdown("### Risco Global Acumulado (Output)")
                df_grafico = preparar_dados_grafico(
                    risco_fifo, risco_gulosa, risco_a_star
                )

                fig_risco = px.bar(
                    df_grafico,
                    x="Risco Global Acumulado",
                    y="Estratégia",
                    orientation="h",
                    color="Estratégia",
                    text="Risco Global Acumulado",
                    color_discrete_map={
                        "Aproximação FIFO": "#636EFA",
                        "Heurística Gulosa": "#EF553B",
                        "Busca A* (Otimizador)": "#00CC96",
                    },
                )

                min_risco = df_grafico["Risco Global Acumulado"].min()
                max_risco = df_grafico["Risco Global Acumulado"].max()
                margem = (
                    (max_risco - min_risco) * 0.5
                    if max_risco != min_risco
                    else max_risco * 0.1
                )

                fig_risco.update_layout(
                    xaxis=dict(range=[max(0, min_risco - margem), max_risco + margem]),
                    xaxis_title="Risco Numérico",
                    yaxis_title=None,
                    showlegend=False,
                    margin=dict(t=20, b=0, l=0, r=0),
                )
                fig_risco.update_traces(
                    texttemplate="%{text:,.2f}", textposition="outside"
                )

                st.plotly_chart(fig_risco, use_container_width=True)

        with aba_auditoria:
            st.markdown("### Exportação e Auditoria de Resultados")
            st.info(
                "Utilize as tabelas abaixo para auditar a ordem de atendimento gerada por cada algoritmo ou exporte os dados no formato CSV para softwares estatísticos."
            )

            df_a_star_audit = gerar_dataframe_auditoria(lista_pacientes, ordem_a_star)

            csv_data = df_a_star_audit.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Baixar Dados da Fila A* (CSV)",
                data=csv_data,
                file_name="auditoria_fila_a_star.csv",
                mime="text/csv",
            )

            st.markdown("#### Matriz de Permutação: Busca A*")
            st.dataframe(df_a_star_audit, use_container_width=True)

            st.markdown("#### Matriz de Permutação: Heurística Gulosa")
            df_gulosa_audit = gerar_dataframe_auditoria(lista_pacientes, ordem_gulosa)
            st.dataframe(df_gulosa_audit, use_container_width=True)

            st.markdown("#### Matriz de Permutação: Aproximação FIFO")
            df_fifo_audit = gerar_dataframe_auditoria(lista_pacientes, ordem_fifo)
            st.dataframe(df_fifo_audit, use_container_width=True)

rodape_html = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    .standard-footer {
        margin-top: 50px;
        padding: 20px 0;
        border-top: 1px solid #e6e6e6;
        color: #666;
        font-family: sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: transparent;
    }

    /* Suporte nativo para Modo Escuro do Streamlit */
    @media (prefers-color-scheme: dark) {
        .standard-footer {
            border-top: 1px solid #2b2b36;
            color: #a0a0a0;
        }
    }

    .standard-footer .footer-text {
        margin-bottom: 12px;
        font-size: 14px;
        text-align: center;
    }

    .standard-footer .footer-links {
        display: flex;
        gap: 24px;
        justify-content: center;
        flex-wrap: wrap;
    }

    .standard-footer a {
        color: #00CC96;
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        transition: color 0.3s ease;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .standard-footer a:hover {
        color: #009970;
    }
</style>

<div class="standard-footer">
    <div class="footer-text">
        <strong>© 2026 Desenvolvido por Hugo Mendes</strong>
    </div>
    <div class="footer-links">
        <a href="https://github.com/fhugomp" target="_blank"><i class="fab fa-github"></i> GitHub</a>
        <a href="https://linkedin.com/in/fhugomp" target="_blank"><i class="fab fa-linkedin"></i> LinkedIn</a>
        <a href="https://fhugomp.github.io" target="_blank"><i class="fas fa-globe"></i> Portfólio Profissional</a>
    </div>
</div>
"""

st.markdown(rodape_html, unsafe_allow_html=True)
