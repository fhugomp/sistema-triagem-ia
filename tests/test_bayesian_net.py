import pytest
from pgmpy.factors.discrete import TabularCPD
from typing import cast
from src.models.bayesian_net import SistemaTriagemBayesiana


@pytest.fixture
def rbn_sistema() -> SistemaTriagemBayesiana:
    return SistemaTriagemBayesiana()


def test_hard_flags_variaveis_e_estados(rbn_sistema: SistemaTriagemBayesiana) -> None:
    """
    Garante as flags:
    - Exatas 6 variáveis de entrada e +1 de saída (Gravidade).
    - Nó central "Gravidade" com 3 estados: baixa, média, alta.
    """
    cpd_gravidade = cast(TabularCPD, rbn_sistema.model.get_cpds("Gravidade"))
    estados_gravidade = cpd_gravidade.state_names["Gravidade"]
    assert estados_gravidade == [
        "baixa",
        "média",
        "alta",
    ], "Falha na Hard Flag 3: Nomenclatura dos estados incorreta!"

    variaveis_modelo = rbn_sistema.model.nodes()
    variaveis_esperadas = [
        "IdadeAvancada",
        "DoencaCronica",
        "SaturacaoO2",
        "FrequenciaCardiaca",
        "NivelDor",
        "Febre",
        "Gravidade",
    ]
    assert set(variaveis_modelo) == set(
        variaveis_esperadas
    ), "Falha nas Hard Flags 1 e 2: Estrutura de variáveis inválida!"


def test_inferencia_paciente_critico(rbn_sistema: SistemaTriagemBayesiana) -> None:
    """
    Garante que um paciente com todas as flags anormais receba altíssima probabilidade de gravidade ALTA.
    Atende à recomendação de validação da ordem de iteração da CPT do Pgmpy.
    """
    evidencias = {
        "IdadeAvancada": "Verdadeiro",
        "DoencaCronica": "Verdadeiro",
        "SaturacaoO2": "Baixa",
        "FrequenciaCardiaca": "Alta",
        "NivelDor": "Intensa",
        "Febre": "Presente",
    }
    probabilidades = rbn_sistema.calcular_probabilidade_gravidade(evidencias)
    assert (
        probabilidades["alta"] > 0.85
    ), "A probabilidade de alta gravidade deve ser esmagadora para um paciente crítico total!"


def test_inferencia_paciente_saudavel(rbn_sistema: SistemaTriagemBayesiana) -> None:
    """
    Garante que um paciente sem nenhuma flag anormal receba altíssima probabilidade de gravidade BAIXA.
    Atende à recomendação de validação da ordem de iteração da CPT do Pgmpy.
    """
    evidencias = {
        "IdadeAvancada": "Falso",
        "DoencaCronica": "Falso",
        "SaturacaoO2": "Normal",
        "FrequenciaCardiaca": "Normal",
        "NivelDor": "Leve",
        "Febre": "Ausente",
    }
    probabilidades = rbn_sistema.calcular_probabilidade_gravidade(evidencias)
    assert (
        probabilidades["baixa"] > 0.70
    ), "A probabilidade de baixa gravidade deve ser dominante para um paciente sem anormalidades!"


def test_comportamento_com_evidencias_incompletas(
    rbn_sistema: SistemaTriagemBayesiana,
) -> None:
    """
    Verifica se o sistema consegue inferir e marginalizar corretamente quando
    nem todos os dados clínicos foram aferidos na triagem inicial.
    """
    evidencias_parciais = {
        "IdadeAvancada": "Verdadeiro",
        "SaturacaoO2": "Baixa",
    }
    probabilidades = rbn_sistema.calcular_probabilidade_gravidade(evidencias_parciais)

    assert "baixa" in probabilidades
    assert "média" in probabilidades
    assert "alta" in probabilidades

    # A soma das marginais deve sempre resultar em 1.0 (fechamento probabilístico)
    soma = sum(probabilidades.values())
    assert (
        abs(soma - 1.0) < 1e-6
    ), "O fechamento probabilístico falhou em evidências parciais!"
