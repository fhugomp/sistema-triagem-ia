"""
Módulo de orquestração da simulação de triagem.
Executa o pipeline: Geração → Inferência Bayesiana → Otimização → Resultados.
"""

from dataclasses import dataclass
from typing import cast, Literal, List, Dict, Any

from src.data.generator import GeradorPacientesSinteticos
from src.models.bayesian_net import SistemaTriagemBayesiana
from src.models.paciente import Paciente
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem


@dataclass
class ResultadoSimulacao:
    """Estrutura imutável com os resultados completos de uma execução de simulação."""

    lista_pacientes: List[Paciente]
    ordem_fifo: List[int]
    risco_fifo: float
    ordem_gulosa: List[int]
    risco_gulosa: float
    ordem_a_star: List[int]
    risco_a_star: float


def enriquecer_com_probabilidades(
    pacientes: List[Paciente], rbn: SistemaTriagemBayesiana
) -> List[Paciente]:
    """Enriquece a lista de pacientes com a probabilidade de gravidade alta
    calculada pela Rede Bayesiana.

    Args:
        pacientes: Lista de objetos Paciente gerados.
        rbn: Instância do sistema de triagem bayesiana.

    Returns:
        Lista enriquecida com cópias atualizadas dos pacientes.
    """
    pacientes_enriquecidos = []
    for p in pacientes:
        probs = rbn.calcular_probabilidade_gravidade(p)
        prob_alta = probs["alta"] if probs else 0.0
        # Pydantic models are frozen, so we use model_copy(update=...)
        p_enriquecido = p.model_copy(update={"probabilidade_alta": prob_alta})
        pacientes_enriquecidos.append(p_enriquecido)

    return pacientes_enriquecidos


def executar_simulacao(
    num_pacientes: int,
    tipo_funcao: Literal["linear", "exponencial"],
    estrategia_particionamento: Literal["fifo", "risco_inicial"],
    usar_janela: bool,
    gerador: GeradorPacientesSinteticos,
    rbn: SistemaTriagemBayesiana,
    a_star: OtimizadorTriagemAStar,
    baselines: BaselinesTriagem,
) -> ResultadoSimulacao:
    """Executa o pipeline completo de simulação de triagem.

    Args:
        num_pacientes: Número de pacientes a gerar.
        tipo_funcao: Modelo de deterioração clínica.
        estrategia_particionamento: Heurística de particionamento do A*.
        usar_janela: Se True, ativa o modo Sliding Window do A*.
        gerador: Instância do gerador de pacientes.
        rbn: Instância do sistema de triagem bayesiana.
        a_star: Instância do otimizador A*.
        baselines: Instância das estratégias baseline.

    Returns:
        ResultadoSimulacao com todas as ordens e riscos calculados.
    """
    # Passo A: Geração de Dados e Inferência Bayesiana
    lista_pacientes = gerador.gerar_pacientes(num_pacientes)
    lista_pacientes = enriquecer_com_probabilidades(lista_pacientes, rbn)

    # Passo B: Execução Simultânea das Estratégias
    ordem_fifo, risco_fifo = baselines.simular_fifo(lista_pacientes.copy(), tipo_funcao)
    ordem_gulosa, risco_gulosa = baselines.simular_gulosa(
        lista_pacientes.copy(), tipo_funcao
    )
    ordem_a_star, risco_a_star = a_star.otimizar_fila(
        lista_pacientes.copy(),
        tipo_funcao=tipo_funcao,
        estrategia_particionamento=estrategia_particionamento,
        usar_janela=usar_janela,
    )

    return ResultadoSimulacao(
        lista_pacientes=lista_pacientes,
        ordem_fifo=ordem_fifo,
        risco_fifo=risco_fifo,
        ordem_gulosa=ordem_gulosa,
        risco_gulosa=risco_gulosa,
        ordem_a_star=ordem_a_star,
        risco_a_star=risco_a_star,
    )
