import pytest
import pandas as pd
from src.data.generator import GeradorPacientesSinteticos


@pytest.fixture
def gerador() -> GeradorPacientesSinteticos:
    """Instancia o gerador com uma seed fixa para testes determinísticos."""
    return GeradorPacientesSinteticos(seed=13)


def test_tamanho_e_colunas_dataframe(gerador: GeradorPacientesSinteticos) -> None:
    """Garante que a base sintética atende aos requisitos de tamanho e estrutura."""
    num_pacientes = 50
    df = gerador.gerar_pacientes(num_pacientes)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == num_pacientes

    colunas_esperadas = [
        "ID_Paciente",
        "Idade_Anos",
        "IdadeAvancada",
        "DoencaCronica",
        "SaturacaoO2",
        "FrequenciaCardiaca",
        "NivelDor",
        "Febre",
        "TempoEspera_Inicial_Minutos",
    ]
    assert list(df.columns) == colunas_esperadas


def test_compatibilidade_com_rede_bayesiana(
    gerador: GeradorPacientesSinteticos,
) -> None:
    """
    Garante que as strings geradas pelo Pandas são exatamentes as mesmas
    exigidas pelas variáveis da nossa Rede Bayesiana.
    """
    df = gerador.gerar_pacientes(10)

    assert set(df["IdadeAvancada"].unique()).issubset({"Falso", "Verdadeiro"})
    assert set(df["SaturacaoO2"].unique()).issubset({"Normal", "Baixa"})
    assert set(df["FrequenciaCardiaca"].unique()).issubset({"Normal", "Alta"})
    assert set(df["NivelDor"].unique()).issubset({"Leve", "Intensa"})
    assert set(df["Febre"].unique()).issubset({"Ausente", "Presente"})
