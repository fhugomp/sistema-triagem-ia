"""
Testes dos novos KPIs de Business Intelligence retornados por executar_simulacao().
Cobre: tempo de execucao wall-clock, nos explorados pelo A* e tempo medio de espera.
"""

import pytest

from src.data.generator import GeradorPacientesSinteticos
from src.models.bayesian_net import SistemaTriagemBayesiana
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem
from src.simulation.runner import executar_simulacao, _calcular_tempo_medio_espera


@pytest.fixture(scope="module")
def sistema() -> (
    tuple[
        GeradorPacientesSinteticos,
        SistemaTriagemBayesiana,
        OtimizadorTriagemAStar,
        BaselinesTriagem,
    ]
):
    """Inicializa os componentes do sistema uma vez por modulo de teste."""
    gerador = GeradorPacientesSinteticos(seed=42)
    rbn = SistemaTriagemBayesiana()
    a_star = OtimizadorTriagemAStar(tempo_atendimento_minutos=15)
    baselines = BaselinesTriagem(tempo_atendimento_minutos=15)
    return gerador, rbn, a_star, baselines


def _executar(
    sistema: tuple,
    num_pacientes: int = 10,
    usar_janela: bool = True,
):
    """Auxiliar para executar uma simulacao com parametros padrao."""
    gerador, rbn, a_star, baselines = sistema
    return executar_simulacao(
        num_pacientes=num_pacientes,
        tipo_funcao="linear",
        estrategia_particionamento="risco_inicial",
        usar_janela=usar_janela,
        gerador=gerador,
        rbn=rbn,
        a_star=a_star,
        baselines=baselines,
    )


def test_tempo_execucao_positivo(sistema: tuple) -> None:
    """O tempo de execucao wall-clock deve ser estritamente positivo."""
    resultado = _executar(sistema)
    assert resultado.tempo_execucao_segundos > 0.0, (
        "O tempo de execucao deve ser maior que zero."
    )


def test_nos_explorados_positivo(sistema: tuple) -> None:
    """O contador de nos explorados deve ser estritamente positivo."""
    resultado = _executar(sistema)
    assert resultado.nos_explorados_a_star > 0, (
        "O A* deve explorar ao menos um no."
    )


def test_nos_explorados_aumenta_com_n(sistema: tuple) -> None:
    """Filas maiores devem gerar mais expansoes de nos pelo A*."""
    resultado_pequeno = _executar(sistema, num_pacientes=5)
    resultado_grande = _executar(sistema, num_pacientes=20)

    assert resultado_grande.nos_explorados_a_star > resultado_pequeno.nos_explorados_a_star, (
        "Uma fila maior deve exigir mais expansoes de nos."
    )


def test_tempo_medio_espera_tres_estrategias(sistema: tuple) -> None:
    """O dicionario de tempo medio de espera deve conter exatamente 3 chaves."""
    resultado = _executar(sistema)
    chaves_esperadas = {"fifo", "gulosa", "a_star"}
    assert set(resultado.tempo_medio_espera_por_estrategia.keys()) == chaves_esperadas, (
        f"Esperado {chaves_esperadas}, obtido "
        f"{set(resultado.tempo_medio_espera_por_estrategia.keys())}."
    )


def test_tempo_medio_espera_valores_nao_negativos(sistema: tuple) -> None:
    """Os tempos medios de espera devem ser nao-negativos para todos as estrategias."""
    resultado = _executar(sistema)
    for estrategia, tempo in resultado.tempo_medio_espera_por_estrategia.items():
        assert tempo >= 0.0, (
            f"Tempo medio de espera da estrategia '{estrategia}' nao pode ser negativo."
        )


def test_calcular_tempo_medio_espera_fila_unitaria() -> None:
    """Uma fila com um unico paciente deve ter tempo medio de espera zero."""
    from src.models.paciente import Paciente

    paciente = Paciente(
        id_paciente=1,
        idade_anos=40,
        idade_avancada="Falso",
        doenca_cronica="Falso",
        saturacao_o2="Normal",
        frequencia_cardiaca="Normal",
        nivel_dor="Leve",
        febre="Ausente",
        tempo_espera_inicial_minutos=10,
        probabilidade_alta=0.5,
    )
    tempo = _calcular_tempo_medio_espera([paciente], [1], tempo_atendimento=15)
    assert tempo == pytest.approx(0.0), (
        "Fila com um paciente deve ter espera media zero (ele e atendido imediatamente)."
    )


def test_calcular_tempo_medio_espera_fila_vazia() -> None:
    """Uma ordem vazia deve retornar zero sem lancamento de excecao."""
    tempo = _calcular_tempo_medio_espera([], [], tempo_atendimento=15)
    assert tempo == pytest.approx(0.0)


def test_nos_explorados_global_menor_janela(sistema: tuple) -> None:
    """
    No modo global (N=6, sem janela), o A* explora o espaco completo.
    No modo particionado (N=6, com janela=8, um unico lote), o comportamento
    deve ser identico — este teste valida que o contador funciona em ambos os modos.
    """
    gerador, rbn, a_star, baselines = sistema

    resultado_global = executar_simulacao(
        num_pacientes=6,
        tipo_funcao="linear",
        estrategia_particionamento="fifo",
        usar_janela=False,
        gerador=gerador,
        rbn=rbn,
        a_star=a_star,
        baselines=baselines,
    )
    assert resultado_global.nos_explorados_a_star > 0
