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
    Validação Empírica (Miopia): Comprova que o particionamento temporal do A* (Sliding Window)
    em cenários de superlotação (N=30) produz risco sistematicamente inferior à fila inercial (FIFO).
    """
    df_pacientes = gerador.gerar_pacientes(30)

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

    _, risco_fifo = baselines.simular_fifo(lista_pacientes.copy(), tipo_funcao="linear")
    _, risco_a_star = a_star.otimizar_fila(
        lista_pacientes.copy(),
        tipo_funcao="linear",
        usar_janela=True,
        estrategia_particionamento="fifo",
    )

    assert (
        risco_a_star <= risco_fifo
    ), "O algoritmo A* particionado deve superar a inércia do modelo FIFO."


def test_prova_otimalidade_a_star_global(
    gerador: GeradorPacientesSinteticos,
    rbn_sistema: SistemaTriagemBayesiana,
    a_star: OtimizadorTriagemAStar,
    baselines: BaselinesTriagem,
) -> None:
    """
    Validação da Visibilidade Global:
    Comprova que, ao desativar o particionamento em uma amostra tratável (N=6),
    o A* explora o espaço completo e atinge solução igual ou melhor à heurística Gulosa.
    """
    df_pacientes = gerador.gerar_pacientes(6)

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

    _, risco_gulosa = baselines.simular_gulosa(
        lista_pacientes.copy(), tipo_funcao="linear"
    )
    _, risco_a_star_global = a_star.otimizar_fila(
        lista_pacientes.copy(), tipo_funcao="linear", usar_janela=False
    )

    assert (
        risco_a_star_global <= risco_gulosa
    ), "Falha matemática: O A* global deve obrigatoriamente empatar ou superar a heurística Gulosa."


def test_cobertura_heuristica_risco_inicial(
    gerador: GeradorPacientesSinteticos,
    a_star: OtimizadorTriagemAStar,
) -> None:
    """
    Validação de Integridade de Ramificação:
    Garante que a heurística mitigadora (Risco Inicial) mapeia o particionamento
    sem omissão ou duplicação de entidades.
    """
    df_pacientes = gerador.gerar_pacientes(15)

    # Injeção estática paramétrica para teste isolado de infraestrutura de ordenação
    df_pacientes["Probabilidade_Alta"] = 0.5
    df_pacientes["TempoEspera_Inicial_Minutos"] = 10
    lista_pacientes = cast(List[Dict[str, Any]], df_pacientes.to_dict("records"))

    ordem_a_star, risco_a_star = a_star.otimizar_fila(
        lista_pacientes.copy(),
        tipo_funcao="linear",
        estrategia_particionamento="risco_inicial",
        usar_janela=True,
    )

    assert (
        len(ordem_a_star) == 15
    ), "A heurística de risco inicial omitiu ou duplicou pacientes."
    assert (
        risco_a_star > 0.0
    ), "O risco acumulado falhou ao ser computado na heurística mitigadora."
