import math
from typing import List, Dict, Any, Tuple, Literal
from src import config


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
        ordem_pacientes: List[Dict[str, Any]],
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
    ) -> Tuple[List[int], float]:
        """
        Calcula o risco total de uma ordem de pacientes, suportando funções lineares e exponenciais.
        """
        risco_total = 0.0
        tempo_atual = 0
        ordem_ids = []

        for p in ordem_pacientes:
            tempo_espera_real = tempo_atual + p["TempoEspera_Inicial_Minutos"]

            if tipo_funcao == "exponencial":
                risco_paciente = p["Probabilidade_Alta"] * math.exp(
                    tempo_espera_real / config.TAU_EXPONENCIAL
                )
            else:
                risco_paciente = p["Probabilidade_Alta"] * tempo_espera_real

            risco_total += risco_paciente
            ordem_ids.append(p["ID_Paciente"])
            tempo_atual += self.tempo_atendimento_minutos

        return ordem_ids, risco_total

    def simular_fifo(
        self,
        pacientes: List[Dict[str, Any]],
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
    ) -> Tuple[List[int], float]:
        pacientes_ordenados = sorted(
            pacientes, key=lambda x: x["TempoEspera_Inicial_Minutos"], reverse=True
        )
        return self._calcular_risco_total(pacientes_ordenados, tipo_funcao)

    def simular_gulosa(
        self,
        pacientes: List[Dict[str, Any]],
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
    ) -> Tuple[List[int], float]:
        pacientes_ordenados = sorted(
            pacientes, key=lambda x: x["Probabilidade_Alta"], reverse=True
        )
        return self._calcular_risco_total(pacientes_ordenados, tipo_funcao)
