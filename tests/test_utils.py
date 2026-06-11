import pandas as pd
from src.utils import preparar_dados_grafico, gerar_dataframe_auditoria

def test_preparar_dados_grafico_estrutura() -> None:
    """
    Garante que o preparador de dados para o gráfico gera a estrutura Tidy
    correta, sem omissão de parâmetros ou falha de nomenclatura.
    """
    df_grafico = preparar_dados_grafico(150.5, 90.2, 90.2)
    
    assert len(df_grafico) == 3, "O gráfico deve conter exatamente três eixos comparativos."
    assert "Estratégia" in df_grafico.columns, "Coluna categórica ausente."
    assert "Risco Global Acumulado" in df_grafico.columns, "Coluna de valor ausente."
    assert df_grafico.iloc[2]["Risco Global Acumulado"] == 90.2, "Falha no mapeamento do risco A*."


def test_gerar_dataframe_auditoria_ordenacao() -> None:
    """
    Valida a transposição matricial: assegura que o gerador de auditoria
    aplica a permutação correta sem corromper os dados dos pacientes.
    """
    pacientes_mock = [
        {"ID_Paciente": 101, "Risco": 10, "Nome": "A"},
        {"ID_Paciente": 102, "Risco": 50, "Nome": "B"},
        {"ID_Paciente": 103, "Risco": 90, "Nome": "C"}
    ]
    ordem_calculada = [103, 101, 102]
    
    df_audit = gerar_dataframe_auditoria(pacientes_mock, ordem_calculada)
    
    assert len(df_audit) == 3, "Perda de dados durante a ordenação."
    assert df_audit.iloc[0]["ID_Paciente"] == 103, "Falha de ordenação posicional (Índice 0)."
    assert df_audit.iloc[0]["Nome"] == "C", "Falha de integridade dos dados na transposição."
    assert df_audit.iloc[-1]["ID_Paciente"] == 102, "Falha de ordenação posicional (Índice N)."