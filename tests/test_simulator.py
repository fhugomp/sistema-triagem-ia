import pytest
from typing import cast, List, Dict, Any

from src.data.generator import GeradorPacientesSinteticos
from src.models.bayesian_net import SistemaTriagemBayesiana
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem


@pytest.fixture
def gerador() -> GeradorPacientesSinteticos:
    return GeradorPacientesSinteticos(seed=42)


@pytest.fixture
def rbn_sistema() -> SistemaTriagemBayesiana:
    return SistemaTriagemBayesiana()


@pytest.fixture
def a_star() -> OtimizadorTriagemAStar:
    return OtimizadorTriagemAStar(tempo_atendimento_minutos=15)


@pytest.fixture
def baselines() -> BaselinesTriagem:
    return BaselinesTriagem(tempo_atendimento_minutos=15)


def test_hard_flag_comparativo_estrategias(
    gerador: GeradorPacientesSinteticos,
    rbn_sistema: SistemaTriagemBayesiana,
    a_star: OtimizadorTriagemAStar,
    baselines: BaselinesTriagem,
) -> None:
    """
    Validação Empírica: Comprova que o particionamento do A* produz um risco global sistemicamente inferior à fila inercial (FIFO).
    Devido à miopia do particionamento, não se garante vitória empírica contra
    a estratégia Gulosa em 100% das vezes.
    """
    df_pacientes = gerador.gerar_pacientes(30)

    # 1. Inferência Bayesiana para calcular o Risco Inicial
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
        probs = rbn_sistema.calcular_probabilidade_gravidade(evidencias)
        probabilidades_alta.append(probs["alta"] if probs else 0.0)

    df_pacientes["Probabilidade_Alta"] = probabilidades_alta
    lista_pacientes = cast(List[Dict[str, Any]], df_pacientes.to_dict("records"))

    # 2. Execução Simulânea
    _, risco_fifo = baselines.simular_fifo(lista_pacientes.copy(), tipo_funcao="linear")
    _, risco_gulosa = baselines.simular_gulosa(
        lista_pacientes.copy(), tipo_funcao="linear"
    )
    _, risco_a_star = a_star.otimizar_fila(lista_pacientes.copy(), tipo_funcao="linear")

    # 3. Validação do Limite Acadêmico (Superar a inércia do FIFO)
    assert (
        risco_a_star <= risco_fifo
    ), "O algoritmo A* com janela deve produzir um risco sistematicamente inferior ao FIFO!"
