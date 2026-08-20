from typing import List, Tuple, Literal
from src import config
from src.optimization.risk import calcular_risco
from src.models.paciente import Paciente


class BaselinesTriagem:
    """
    Classe para simular diferentes estratégias de triagem de pacientes.
    """

    def __init__(
        self, tempo_atendimento_minutos: int = config.TEMPO_ATENDIMENTO_MINUTOS
    ):
        self.tempo_atendimento_minutos = tempo_atendimento_minutos

    def _calcular_risco_total(
        self,
        ordem_pacientes: List[Paciente],
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
    ) -> Tuple[List[int], float]:
        """
        Calcula o risco total de uma ordem de pacientes, suportando funções lineares e exponenciais.
        """
        risco_total = 0.0
        tempo_atual = 0
        ordem_ids = []

        for p in ordem_pacientes:
            tempo_espera_real = tempo_atual + p.tempo_espera_inicial_minutos
            risco_paciente = calcular_risco(
                p.probabilidade_alta, tempo_espera_real, tipo_funcao
            )

            risco_total += risco_paciente
            ordem_ids.append(p.id_paciente)
            tempo_atual += self.tempo_atendimento_minutos

        return ordem_ids, risco_total

    def simular_fifo(
        self,
        pacientes: List[Paciente],
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
    ) -> Tuple[List[int], float]:
        pacientes_ordenados = sorted(
            pacientes, key=lambda x: x.tempo_espera_inicial_minutos, reverse=True
        )
        return self._calcular_risco_total(pacientes_ordenados, tipo_funcao)

    def simular_gulosa(
        self,
        pacientes: List[Paciente],
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
    ) -> Tuple[List[int], float]:
        pacientes_ordenados = sorted(
            pacientes, key=lambda x: x.probabilidade_alta, reverse=True
        )
        return self._calcular_risco_total(pacientes_ordenados, tipo_funcao)
