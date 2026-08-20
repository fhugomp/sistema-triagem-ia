"""
Componentes de interface Streamlit para o Sistema de Triagem.
Funções puras de renderização que recebem dados e escrevem na tela.
"""

import streamlit as st
import plotly.express as px
from typing import List

from src.models.paciente import Paciente
from src.simulation.runner import ResultadoSimulacao
from src.utils import (
    preparar_dados_grafico,
    gerar_dataframe_auditoria,
    preparar_dados_perfil_clinico,
)


def formatar_numero_br(valor: float) -> str:
    """Formata um número float para o padrão brasileiro (1.234,56)."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def renderizar_metricas(resultado: ResultadoSimulacao) -> None:
    """Renderiza os cards de métricas comparativas entre as estratégias."""
    delta_matematico = resultado.risco_a_star - resultado.risco_gulosa

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Aproximação FIFO",
            value=formatar_numero_br(resultado.risco_fifo),
        )
    with col2:
        st.metric(
            label="Heurística Gulosa",
            value=formatar_numero_br(resultado.risco_gulosa),
        )
    with col3:
        st.metric(
            label="Busca A* (Otimizador)",
            value=formatar_numero_br(resultado.risco_a_star),
            delta=f"{delta_matematico:+.2f} vs Gulosa",
            delta_color="inverse",
        )


def renderizar_grafico_perfil_clinico(
    lista_pacientes: List[Paciente],
) -> None:
    """Renderiza o histograma de distribuição de risco clínico (input da Rede Bayesiana)."""
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


def renderizar_grafico_risco_acumulado(resultado: ResultadoSimulacao) -> None:
    """Renderiza o gráfico de barras comparativo do risco acumulado global."""
    st.markdown("### Risco Global Acumulado (Output)")
    df_grafico = preparar_dados_grafico(
        resultado.risco_fifo, resultado.risco_gulosa, resultado.risco_a_star
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
        (max_risco - min_risco) * 0.5 if max_risco != min_risco else max_risco * 0.1
    )

    fig_risco.update_layout(
        xaxis=dict(range=[max(0, min_risco - margem), max_risco + margem]),
        xaxis_title="Risco Numérico",
        yaxis_title=None,
        showlegend=False,
        margin=dict(t=20, b=0, l=0, r=0),
    )
    fig_risco.update_traces(texttemplate="%{text:,.2f}", textposition="outside")

    st.plotly_chart(fig_risco, use_container_width=True)


def renderizar_aba_executiva(resultado: ResultadoSimulacao) -> None:
    """Renderiza a aba 'Visão Executiva' com métricas e gráficos."""
    renderizar_metricas(resultado)
    st.markdown("---")

    grafico_esq, grafico_dir = st.columns(2)
    with grafico_esq:
        renderizar_grafico_perfil_clinico(resultado.lista_pacientes)
    with grafico_dir:
        renderizar_grafico_risco_acumulado(resultado)


def renderizar_aba_auditoria(resultado: ResultadoSimulacao) -> None:
    """Renderiza a aba 'Auditoria de Fila' com tabelas e export CSV."""
    st.markdown("### Exportação e Auditoria de Resultados")
    st.info(
        "Utilize as tabelas abaixo para auditar a ordem de atendimento gerada por "
        "cada algoritmo ou exporte os dados no formato CSV para softwares estatísticos."
    )

    df_a_star_audit = gerar_dataframe_auditoria(
        resultado.lista_pacientes, resultado.ordem_a_star
    )

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
    df_gulosa_audit = gerar_dataframe_auditoria(
        resultado.lista_pacientes, resultado.ordem_gulosa
    )
    st.dataframe(df_gulosa_audit, use_container_width=True)

    st.markdown("#### Matriz de Permutação: Aproximação FIFO")
    df_fifo_audit = gerar_dataframe_auditoria(
        resultado.lista_pacientes, resultado.ordem_fifo
    )
    st.dataframe(df_fifo_audit, use_container_width=True)


def renderizar_resultados(resultado: ResultadoSimulacao) -> None:
    """Renderiza toda a seção de resultados com abas."""
    st.markdown("---")
    st.header("📊 Análise de Desempenho do Escalonamento")

    aba_executiva, aba_auditoria = st.tabs(
        [
            "Visão Executiva (Métricas e Gráficos)",
            "Auditoria de Fila (Dados Brutos)",
        ]
    )

    with aba_executiva:
        renderizar_aba_executiva(resultado)

    with aba_auditoria:
        renderizar_aba_auditoria(resultado)


def renderizar_rodape() -> None:
    """Renderiza o rodapé HTML com links do autor."""
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
