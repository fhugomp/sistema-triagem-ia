import pandas as pd
from typing import List, Dict, Any

def preparar_dados_grafico(risco_fifo: float, risco_gulosa: float, risco_a_star: float) -> pd.DataFrame:
    """
    Estrutura os riscos acumulados em um formato tabular longo (Tidy Data),
    otimizado para a renderização de gráficos comparativos nativos.
    """
    return pd.DataFrame({
        "Estratégia": ["Aproximação FIFO", "Heurística Gulosa", "Busca A* (Otimizador)"],
        "Risco Global Acumulado": [risco_fifo, risco_gulosa, risco_a_star]
    })

def gerar_dataframe_auditoria(lista_pacientes: List[Dict[str, Any]], ordem_atendimento: List[int]) -> pd.DataFrame:
    """
    Reordena o conjunto original de pacientes com base na matriz de permutação
    gerada pelos algoritmos de otimização, preparando para exportação.
    """
    df = pd.DataFrame(lista_pacientes)
    df.set_index("ID_Paciente", inplace=True)
    df_ordenado = df.loc[ordem_atendimento].reset_index()
    return df_ordenado