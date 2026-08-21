"""
Modulo de orquestracao da simulacao de triagem.
Executa o pipeline: Geracao -> Inferencia Bayesiana -> Otimizacao -> Resultados.
"""

import time
from dataclasses import dataclass, field
from typing import cast, Generator, Literal, List, Dict

from src.data.generator import GeradorPacientesSinteticos
from src.models.bayesian_net import SistemaTriagemBayesiana
from src.models.paciente import Paciente
from src.optimization.a_star import OtimizadorTriagemAStar
from src.optimization.baselines import BaselinesTriagem


@dataclass
class ResultadoSimulacao:
    """Estrutura imutavel com os resultados completos de uma execucao de simulacao."""

    lista_pacientes: List[Paciente]
    ordem_fifo: List[int]
    risco_fifo: float
    ordem_gulosa: List[int]
    risco_gulosa: float
    ordem_a_star: List[int]
    risco_a_star: float

    # KPIs de Business Intelligence (v2.0)
    tempo_execucao_segundos: float = field(default=0.0)
    nos_explorados_a_star: int = field(default=0)
    tempo_medio_espera_por_estrategia: Dict[str, float] = field(default_factory=dict)


def enriquecer_com_probabilidades(
    pacientes: List[Paciente], rbn: SistemaTriagemBayesiana
) -> List[Paciente]:
    """Enriquece a lista de pacientes com a probabilidade de gravidade alta
    calculada pela Rede Bayesiana.

    Args:
        pacientes: Lista de objetos Paciente gerados.
        rbn: Instancia do sistema de triagem bayesiana.

    Returns:
        Lista enriquecida com copias atualizadas dos pacientes.
    """
    pacientes_enriquecidos = []
    for p in pacientes:
        probs = rbn.calcular_probabilidade_gravidade(p)
        prob_alta = probs["alta"] if probs else 0.0
        # Pydantic models are frozen, so we use model_copy(update=...)
        p_enriquecido = p.model_copy(update={"probabilidade_alta": prob_alta})
        pacientes_enriquecidos.append(p_enriquecido)

    return pacientes_enriquecidos


def _calcular_tempo_medio_espera(
    pacientes: List[Paciente],
    ordem: List[int],
    tempo_atendimento: int,
) -> float:
    """Calcula o tempo medio de espera acumulado para uma dada ordem de atendimento.

    O tempo de espera de um paciente na posicao k da fila e a soma dos tempos
    de atendimento dos (k-1) pacientes anteriores.

    Args:
        pacientes: Lista completa de pacientes com IDs.
        ordem: Sequencia de IDs na ordem de atendimento.
        tempo_atendimento: Duracao fixa de cada atendimento em minutos.

    Returns:
        Media aritmetica dos tempos de espera acumulados em minutos.
    """
    if not ordem:
        return 0.0
    total_espera = sum(posicao * tempo_atendimento for posicao in range(len(ordem)))
    return total_espera / len(ordem)


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
    """Executa o pipeline completo de simulacao de triagem.

    Args:
        num_pacientes: Numero de pacientes a gerar.
        tipo_funcao: Modelo de deterioracao clinica.
        estrategia_particionamento: Heuristica de particionamento do A*.
        usar_janela: Se True, ativa o modo Sliding Window do A*.
        gerador: Instancia do gerador de pacientes.
        rbn: Instancia do sistema de triagem bayesiana.
        a_star: Instancia do otimizador A*.
        baselines: Instancia das estrategias baseline.

    Returns:
        ResultadoSimulacao com todas as ordens, riscos e KPIs de BI calculados.
    """
    inicio = time.perf_counter()

    # Passo A: Geracao de Dados e Inferencia Bayesiana
    lista_pacientes = gerador.gerar_pacientes(num_pacientes)
    lista_pacientes = enriquecer_com_probabilidades(lista_pacientes, rbn)

    # Passo B: Execucao Simultanea das Estrategias
    ordem_fifo, risco_fifo = baselines.simular_fifo(lista_pacientes.copy(), tipo_funcao)
    ordem_gulosa, risco_gulosa = baselines.simular_gulosa(
        lista_pacientes.copy(), tipo_funcao
    )
    ordem_a_star, risco_a_star, nos_explorados = a_star.otimizar_fila(
        lista_pacientes.copy(),
        tipo_funcao=tipo_funcao,
        estrategia_particionamento=estrategia_particionamento,
        usar_janela=usar_janela,
    )

    fim = time.perf_counter()
    tempo_execucao = fim - inicio

    # KPI: Tempo medio de espera acumulado por estrategia
    tempo_medio_espera = {
        "fifo": _calcular_tempo_medio_espera(
            lista_pacientes, ordem_fifo, a_star.tempo_atendimento
        ),
        "gulosa": _calcular_tempo_medio_espera(
            lista_pacientes, ordem_gulosa, a_star.tempo_atendimento
        ),
        "a_star": _calcular_tempo_medio_espera(
            lista_pacientes, ordem_a_star, a_star.tempo_atendimento
        ),
    }

    return ResultadoSimulacao(
        lista_pacientes=lista_pacientes,
        ordem_fifo=ordem_fifo,
        risco_fifo=risco_fifo,
        ordem_gulosa=ordem_gulosa,
        risco_gulosa=risco_gulosa,
        ordem_a_star=ordem_a_star,
        risco_a_star=risco_a_star,
        tempo_execucao_segundos=tempo_execucao,
        nos_explorados_a_star=nos_explorados,
        tempo_medio_espera_por_estrategia=tempo_medio_espera,
    )


@dataclass
class SnapshotSimulacao:
    """Snapshot intermediario do estado da simulacao, emitido pelo gerador de streaming.

    Permite que a interface atualize os graficos frame a frame enquanto o A* processa
    cada lote/janela sem aguardar a conclusao total do pipeline.
    """

    lista_pacientes: List[Paciente]
    ordem_fifo: List[int]
    risco_fifo: float
    ordem_gulosa: List[int]
    risco_gulosa: float
    ordem_a_star_parcial: List[int]
    risco_a_star_parcial: float
    nos_explorados_ate_agora: int
    lote_atual: int
    total_lotes: int
    concluido: bool = False


def executar_simulacao_streaming(
    num_pacientes: int,
    tipo_funcao: Literal["linear", "exponencial"],
    estrategia_particionamento: Literal["fifo", "risco_inicial"],
    usar_janela: bool,
    gerador: GeradorPacientesSinteticos,
    rbn: SistemaTriagemBayesiana,
    a_star: OtimizadorTriagemAStar,
    baselines: BaselinesTriagem,
) -> Generator[SnapshotSimulacao, None, None]:
    """Versao geradora do pipeline de simulacao para visualizacao em streaming.

    Executa o pre-processamento (geracao + inferencia bayesiana + baselines) de forma
    sincrona e, em seguida, faz yield de um SnapshotSimulacao apos cada lote processado
    pelo A*, permitindo atualizacao frame a frame da interface.

    Args:
        num_pacientes: Numero de pacientes a gerar.
        tipo_funcao: Modelo de deterioracao clinica.
        estrategia_particionamento: Heuristica de particionamento do A*.
        usar_janela: Se True, ativa o modo Sliding Window do A*.
        gerador: Instancia do gerador de pacientes.
        rbn: Instancia do sistema de triagem bayesiana.
        a_star: Instancia do otimizador A*.
        baselines: Instancia das estrategias baseline.

    Yields:
        SnapshotSimulacao com o estado parcial (ou completo, no ultimo frame).
    """
    from src import config as cfg

    # Passo A: Geracao e inferencia (sincrono — rapido)
    lista_pacientes = gerador.gerar_pacientes(num_pacientes)
    lista_pacientes = enriquecer_com_probabilidades(lista_pacientes, rbn)

    # Passo B: Baselines (sincrono)
    ordem_fifo, risco_fifo = baselines.simular_fifo(lista_pacientes.copy(), tipo_funcao)
    ordem_gulosa, risco_gulosa = baselines.simular_gulosa(
        lista_pacientes.copy(), tipo_funcao
    )

    # Calcula numero de lotes para exibicao de progresso
    janela = cfg.TAMANHO_JANELA_A_STAR if usar_janela else num_pacientes
    total_lotes = max(1, -(-num_pacientes // janela))  # teto da divisao

    # Passo C: A* com streaming por lote
    for idx, (ordem_parcial, risco_parcial, nos_ate_agora) in enumerate(
        a_star.otimizar_fila_streaming(
            lista_pacientes.copy(),
            tipo_funcao=tipo_funcao,
            estrategia_particionamento=estrategia_particionamento,
            usar_janela=usar_janela,
        ),
        start=1,
    ):
        concluido = idx == total_lotes
        yield SnapshotSimulacao(
            lista_pacientes=lista_pacientes,
            ordem_fifo=ordem_fifo,
            risco_fifo=risco_fifo,
            ordem_gulosa=ordem_gulosa,
            risco_gulosa=risco_gulosa,
            ordem_a_star_parcial=ordem_parcial,
            risco_a_star_parcial=risco_parcial,
            nos_explorados_ate_agora=nos_ate_agora,
            lote_atual=idx,
            total_lotes=total_lotes,
            concluido=concluido,
        )
