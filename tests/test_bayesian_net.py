import pytest
from src.models.bayesian_net import SistemaTriagemBayesiana
from pgmpy.factors.discrete import TabularCPD
from typing import cast


@pytest.fixture
def rbn_sistema() -> SistemaTriagemBayesiana:
    """Fixture para criar uma instância do sistema de triagem bayesiana."""
    return SistemaTriagemBayesiana()


def test_hard_flags_variaveis_e_estados(rbn_sistema: SistemaTriagemBayesiana) -> None:
    """
    Garante as flags:
    - Exatas 5 variáveis de entrada e +1 de saída (Gravidade).
    - Nó central "Gravidade" com 3 estados: baixa, média, alta.
    """
    # Verifica os estados do nó Gravidade
    cpd_gravidade = cast(TabularCPD, rbn_sistema.model.get_cpds("Gravidade"))
    estados_gravidade = cpd_gravidade.state_names["Gravidade"]
    assert estados_gravidade == [
        "baixa",
        "média",
        "alta",
    ], "Falha na Hard Flag 3: Nomenclatura dos estados incorreta!"

    # Verifica as 6 variáveis totais (5 inputs + 1 output)
    variaveis_modelo = rbn_sistema.model.nodes()
    variaveis_esperadas = [
        "IdadeAvancada",
        "Gravidade",
        "SaturacaoO2",
        "FrequenciaCardiaca",
        "NivelDor",
        "Febre",
    ]
    assert set(variaveis_modelo) == set(
        variaveis_esperadas
    ), "Falha nas Hard Flags 1 e 2: Estrutura de variáveis inválida!"


def test_inferencia_paciente_critico(rbn_sistema: SistemaTriagemBayesiana) -> None:
    """
    Testa se um paciente idoso e com todos os sinais vitais alterados
    retorna uma maior probabilidade de gravidade 'alta'.
    Garante a Hard Flag 5 (Vetor probabilístico correto).
    """
    evidencias = {
        "IdadeAvancada": "Verdadeiro",
        "SaturacaoO2": "Baixa",
        "FrequenciaCardiaca": "Alta",
        "NivelDor": "Intensa",
        "Febre": "Presente",
    }

    probabilidades = rbn_sistema.calcular_probabilidade_gravidade(evidencias)

    # Validações matemáticas
    assert probabilidades is not None
    assert sum(probabilidades.values()) == pytest.approx(1.0)
    assert probabilidades["alta"] > probabilidades["média"]
    assert probabilidades["alta"] > probabilidades["baixa"]


def test_inferencia_paciente_saudavel(rbn_sistema: SistemaTriagemBayesiana) -> None:
    """
    Testa se um paciente não idoso e com sinais vitais normais
    retorna uma maior probabilidade de gravidade 'baixa'.
    """
    evidencias = {
        "IdadeAvancada": "Falso",
        "SaturacaoO2": "Normal",
        "FrequenciaCardiaca": "Normal",
        "NivelDor": "Leve",
        "Febre": "Ausente",
    }

    probabilidades = rbn_sistema.calcular_probabilidade_gravidade(evidencias)

    assert probabilidades is not None
    assert probabilidades["baixa"] > probabilidades["alta"]
    assert probabilidades["baixa"] > probabilidades["média"]


def test_comportamento_com_evidencias_incompletas(
    rbn_sistema: SistemaTriagemBayesiana,
) -> None:
    """
    Garante que a rede bayesiana consiga lidar com incertezas (dados faltantes),
    pois na triagem real, nem sempre temos todas as informações.
    """
    # Apenas sabemos a saturação e a idade
    evidencias_parciais = {
        "IdadeAvancada": "Verdadeiro",
        "SaturacaoO2": "Baixa",
    }

    probabilidades = rbn_sistema.calcular_probabilidade_gravidade(evidencias_parciais)
    assert probabilidades is not None
    assert sum(probabilidades.values()) == pytest.approx(1.0)
