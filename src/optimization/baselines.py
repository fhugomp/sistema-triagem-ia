from typing import List, Dict, Any, Tuple


class BaselinesTriagem:
    """
    Classe para simular diferentes estratégias de triagem de pacientes.
    """

    def __init__(self, tempo_atendimento_minutos: int = 15):
        self.tempo_atendimento_minutos = tempo_atendimento_minutos

    def _calcular_risco_total(
        self, ordem_pacientes: List[Dict[str, Any]]
    ) -> Tuple[List[int], float]:
        """
        Calcula o risco total de uma ordem de pacientes.

        Args:
            ordem_pacientes (List[Dict[str, Any]]): Lista de pacientes com suas informações.

        Returns:
            Tuple[List[int], float]: Lista de IDs dos pacientes e o risco total.
        """
        risco_total = 0.0
        tempo_atual = 0
        ordem_ids = []

        for p in ordem_pacientes:
            tempo_espera_real = tempo_atual + p["TempoEspera_Inicial_Minutos"]

            # Risco = P(alta) * f(t)
            risco_paciente = p["Probabilidade_Alta"] * tempo_espera_real
            risco_total += risco_paciente

            ordem_ids.append(p["ID_Paciente"])
            # Tempo de atendimento para o próximo paciente
            tempo_atual += self.tempo_atendimento_minutos

        return ordem_ids, risco_total

    def simular_fifo(self, pacientes: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        pacientes_ordenados = sorted(
            pacientes, key=lambda x: x["TempoEspera_Inicial_Minutos"], reverse=True
        )
        return self._calcular_risco_total(pacientes_ordenados)

    def simular_gulosa(
        self, pacientes: List[Dict[str, Any]]
    ) -> Tuple[List[int], float]:
        pacientes_ordenados = sorted(
            pacientes, key=lambda x: x["Probabilidade_Alta"], reverse=True
        )
        return self._calcular_risco_total(pacientes_ordenados)
