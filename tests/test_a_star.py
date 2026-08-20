import pytest
from src.optimization.a_star import OtimizadorTriagemAStar, NoFila
from src.models.paciente import Paciente


@pytest.fixture
def otimizador() -> OtimizadorTriagemAStar:
    """Instancia o A* com tempo de atendimento padrão de 15 minutos."""
    return OtimizadorTriagemAStar(tempo_atendimento_minutos=15)


@pytest.fixture
def pacientes_mock() -> list[Paciente]:
    """Cria uma mini-fila controlada para testes matemáticos."""
    return [
        Paciente(
            id_paciente=1,
            idade_anos=30,
            idade_avancada="Falso",
            doenca_cronica="Falso",
            saturacao_o2="Normal",
            frequencia_cardiaca="Normal",
            nivel_dor="Leve",
            febre="Ausente",
            tempo_espera_inicial_minutos=10,
            probabilidade_alta=0.8,
        ),
        Paciente(
            id_paciente=2,
            idade_anos=30,
            idade_avancada="Falso",
            doenca_cronica="Falso",
            saturacao_o2="Normal",
            frequencia_cardiaca="Normal",
            nivel_dor="Leve",
            febre="Ausente",
            tempo_espera_inicial_minutos=50,
            probabilidade_alta=0.2,
        ),
        Paciente(
            id_paciente=3,
            idade_anos=30,
            idade_avancada="Falso",
            doenca_cronica="Falso",
            saturacao_o2="Normal",
            frequencia_cardiaca="Normal",
            nivel_dor="Leve",
            febre="Ausente",
            tempo_espera_inicial_minutos=5,
            probabilidade_alta=0.9,
        ),
    ]


def test_calculo_risco(otimizador: OtimizadorTriagemAStar) -> None:
    """Valida a Hard Flag 4: Cálculo rigoroso de Risco = P(Alta) * f(t)"""
    risco = otimizador.calcular_risco_paciente(prob_alta=0.8, tempo_espera=10)
    assert risco == pytest.approx(8.0)


def test_heuristica_admissivel(pacientes_mock: list[Paciente]) -> None:
    """
    Valida a Hard Flag 5: h(n) deve ser a soma dos riscos de todos na fila.
    Matemática esperada:
    P1: 0.8 * 10 = 8.0
    P2: 0.2 * 50 = 10.0
    P3: 0.9 * 5 = 4.5
    Soma h(n) = 22.5
    """
    no = NoFila(
        pacientes_restantes=pacientes_mock,
        risco_acumulado_g=0.0,
        ordem_atendimento=[],
        tempo_atual=0,
    )
    assert no.heuristica_h == pytest.approx(22.5)


def test_comparacao_nos_fila_prioridade() -> None:
    """
    Garante que o método mágico __lt__ funciona para o heapq nativo.
    O heapq deve SEMPRE extrair o nó com o menor custo total f(n).
    """
    no_barato = NoFila([], risco_acumulado_g=10.0, ordem_atendimento=[], tempo_atual=0)
    no_barato.heuristica_h = 5.0
    no_barato.custo_f = 15.0  # f(n) = 15

    no_caro = NoFila([], risco_acumulado_g=20.0, ordem_atendimento=[], tempo_atual=0)
    no_caro.heuristica_h = 10.0
    no_caro.custo_f = 30.0  # f(n) = 30

    assert no_barato < no_caro


def test_a_star_esvazia_fila(
    otimizador: OtimizadorTriagemAStar, pacientes_mock: list[Paciente]
) -> None:
    """Garante que o A* atende todos os pacientes e retorna uma ordem completa."""
    ordem, risco_total = otimizador.otimizar_fila(pacientes_mock)

    # A fila final deve conter exatamente os 3 pacientes iniciais
    assert len(ordem) == 3
    assert set(ordem) == {1, 2, 3}
    assert risco_total > 0.0
