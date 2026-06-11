import pandas as pd
from typing import List, Dict, Any


def preparar_dados_grafico(
    risco_fifo: float, risco_gulosa: float, risco_a_star: float
) -> pd.DataFrame:
    """
    Estrutura os riscos acumulados em um formato tabular longo (Tidy Data),
    aplicando ordenação categórica estrita para a renderização de gráficos.
    """
    df = pd.DataFrame(
        {
            "Estratégia": [
                "Aproximação FIFO",
                "Heurística Gulosa",
                "Busca A* (Otimizador)",
            ],
            "Risco Global Acumulado": [risco_fifo, risco_gulosa, risco_a_star],
        }
    )

    df["Estratégia"] = pd.Categorical(
        df["Estratégia"],
        categories=["Aproximação FIFO", "Heurística Gulosa", "Busca A* (Otimizador)"],
        ordered=True,
    )

    return df.sort_values("Estratégia").reset_index(drop=True)


def gerar_dataframe_auditoria(
    lista_pacientes: List[Dict[str, Any]], ordem_atendimento: List[int]
) -> pd.DataFrame:
    """
    Reordena o conjunto original de pacientes com base na matriz de permutação
    gerada pelos algoritmos de otimização, preparando para exportação.
    """
    df = pd.DataFrame(lista_pacientes)
    df.set_index("ID_Paciente", inplace=True)
    df_ordenado = df.loc[ordem_atendimento].reset_index()
    return df_ordenado


def preparar_dados_perfil_clinico(
    lista_pacientes: List[Dict[str, Any]],
) -> pd.DataFrame:
    """
    Extrai as probabilidades de deterioração clínica e categoriza os níveis de risco
    para visualização da distribuição de entrada (input) da Rede Bayesiana.
    """
    df = pd.DataFrame(lista_pacientes)

    # Definição de limites estatísticos para categorização de risco
    bins = [-0.1, 0.33, 0.66, 1.1]
    labels = ["Baixo Risco", "Risco Moderado", "Alto Risco"]

    df["Categoria de Risco"] = pd.cut(
        df["Probabilidade_Alta"], bins=bins, labels=labels
    )

    # Imposição de ordem categórica para o eixo X do gráfico
    df["Categoria de Risco"] = pd.Categorical(
        df["Categoria de Risco"],
        categories=["Baixo Risco", "Risco Moderado", "Alto Risco"],
        ordered=True,
    )

    return df
