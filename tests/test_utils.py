from src.utils import (
    preparar_dados_grafico,
    gerar_dataframe_auditoria,
    preparar_dados_perfil_clinico,
)


def test_preparar_dados_grafico_estrutura() -> None:
    """
    Garante que o preparador de dados para o gráfico gera a estrutura Tidy
    correta e valida a imposição de ordenação categórica estrita.
    """
    df_grafico = preparar_dados_grafico(150.5, 90.2, 85.0)

    assert (
        len(df_grafico) == 3
    ), "O gráfico deve conter exatamente três eixos comparativos."
    assert "Estratégia" in df_grafico.columns, "Coluna categórica ausente."
    assert "Risco Global Acumulado" in df_grafico.columns, "Coluna de valor ausente."

    # Validação da Ordenação Categórica
    assert (
        df_grafico.iloc[0]["Estratégia"] == "Aproximação FIFO"
    ), "Falha de ordenação (Índice 0)."
    assert (
        df_grafico.iloc[1]["Estratégia"] == "Heurística Gulosa"
    ), "Falha de ordenação (Índice 1)."
    assert (
        df_grafico.iloc[2]["Estratégia"] == "Busca A* (Otimizador)"
    ), "Falha de ordenação (Índice 2)."
    assert (
        df_grafico.iloc[2]["Risco Global Acumulado"] == 85.0
    ), "Falha no mapeamento escalar."


def test_gerar_dataframe_auditoria_ordenacao() -> None:
    """
    Valida a transposição matricial: assegura que o gerador de auditoria
    aplica a permutação correta sem corromper os dados dos pacientes.
    """
    pacientes_mock = [
        {"ID_Paciente": 101, "Risco": 10, "Nome": "A"},
        {"ID_Paciente": 102, "Risco": 50, "Nome": "B"},
        {"ID_Paciente": 103, "Risco": 90, "Nome": "C"},
    ]
    ordem_calculada = [103, 101, 102]

    df_audit = gerar_dataframe_auditoria(pacientes_mock, ordem_calculada)

    assert len(df_audit) == 3, "Perda de dados durante a ordenação."
    assert (
        df_audit.iloc[0]["ID_Paciente"] == 103
    ), "Falha de ordenação posicional (Índice 0)."
    assert (
        df_audit.iloc[0]["Nome"] == "C"
    ), "Falha de integridade dos dados na transposição."
    assert (
        df_audit.iloc[-1]["ID_Paciente"] == 102
    ), "Falha de ordenação posicional (Índice N)."


def test_preparar_dados_perfil_clinico() -> None:
    """
    Valida a extração e a categorização matemática do risco clínico
    para o gráfico de distribuição diagnóstica da Rede Bayesiana.
    """
    pacientes_mock = [
        {"ID_Paciente": 1, "Probabilidade_Alta": 0.10},  # Deve ser Baixo Risco
        {"ID_Paciente": 2, "Probabilidade_Alta": 0.50},  # Deve ser Risco Moderado
        {"ID_Paciente": 3, "Probabilidade_Alta": 0.90},  # Deve ser Alto Risco
    ]

    df_perfil = preparar_dados_perfil_clinico(pacientes_mock)

    assert len(df_perfil) == 3, "Falha na extração dos dados do perfil clínico."
    assert "Categoria de Risco" in df_perfil.columns, "Coluna de categorização ausente."
    assert (
        df_perfil.iloc[0]["Categoria de Risco"] == "Baixo Risco"
    ), "Falha de categorização (Limite Inferior)."
    assert (
        df_perfil.iloc[1]["Categoria de Risco"] == "Risco Moderado"
    ), "Falha de categorização (Mediana)."
    assert (
        df_perfil.iloc[2]["Categoria de Risco"] == "Alto Risco"
    ), "Falha de categorização (Limite Superior)."
