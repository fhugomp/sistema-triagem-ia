import pytest
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem


@pytest.fixture
def pacientes_cenario_critico() -> list[dict]:
    """
    Cenário desenhado especificamente para desafiar os algoritmos:
    - P1: Esperou muito tempo, risco moderado.
    - P2: Acabou de chegar, risco altíssimo (Gulosa atende este primeiro, penalizando P1).
    - P3: Esperou algum tempo, risco baixo.
    """
    return [
        {
            "ID_Paciente": 1,
            "TempoEspera_Inicial_Minutos": 120,
            "Probabilidade_Alta": 0.4,
        },
        {"ID_Paciente": 2, "TempoEspera_Inicial_Minutos": 5, "Probabilidade_Alta": 0.9},
        {
            "ID_Paciente": 3,
            "TempoEspera_Inicial_Minutos": 30,
            "Probabilidade_Alta": 0.1,
        },
    ]


def test_hard_flag_comparativo_estrategias(
    pacientes_cenario_critico: list[dict],
) -> None:
    """
    Condição de Validação Absoluta:
    O A* DEVE matematicamente produzir o menor valor de risco acumulado.
    """
    a_star = OtimizadorTriagemAStar(tempo_atendimento_minutos=15)
    baselines = BaselinesTriagem(tempo_atendimento_minutos=15)

    # .copy() garante que as listas não partilham a mesma referência de memória
    ordem_fifo, risco_fifo = baselines.simular_fifo(pacientes_cenario_critico.copy())
    ordem_gulosa, risco_gulosa = baselines.simular_gulosa(
        pacientes_cenario_critico.copy()
    )
    ordem_a_star, risco_a_star = a_star.otimizar_fila(pacientes_cenario_critico.copy())

    # Garante que as três estratégias devolveram os 3 pacientes
    assert len(ordem_fifo) == 3
    assert len(ordem_gulosa) == 3
    assert len(ordem_a_star) == 3

    # O coração da nossa prova matemática: A* tem de ser superior
    assert (
        risco_a_star <= risco_fifo
    ), f"Falha: A* ({risco_a_star}) pior que FIFO ({risco_fifo})"
    assert (
        risco_a_star <= risco_gulosa
    ), f"Falha: A* ({risco_a_star}) pior que Gulosa ({risco_gulosa})"
