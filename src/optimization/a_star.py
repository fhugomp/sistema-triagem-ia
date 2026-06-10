import heapq
from typing import List, Tuple, Dict, Any


class NoFila:
    """
    Representa um nó na fila de prioridade do algoritmo A*.
    """

    def __init__(
        self,
        pacientes_restantes: List[Dict[str, Any]],
        risco_acumulado_g: float,
        ordem_atendimento: List[int],
        tempo_atual: int,
    ):
        self.pacientes_restantes = pacientes_restantes
        self.risco_acumulado_g = risco_acumulado_g
        self.ordem_atendimento = ordem_atendimento
        self.tempo_atual = tempo_atual

        self.heuristica_h = self.calcular_heuristica()

        self.custo_f = self.risco_acumulado_g + self.heuristica_h

    def calcular_heuristica(self) -> float:
        """
        Método que calcula a heurística (h) para o nó atual, estimando o risco total futuro com base nos pacientes restantes e seus tempos de espera.

        Returns:
            float: A heurística (h) para o nó atual.
        """
        risco_h = 0.0
        for p in self.pacientes_restantes:
            tempo_espera_total = self.tempo_atual + p["TempoEspera_Inicial_Minutos"]
            risco_h += p["Probabilidade_Alta"] * tempo_espera_total
        return risco_h

    def __lt__(self, other: "NoFila") -> bool:
        """
        Método de comparação para a fila de prioridade, baseado no custo f (g + h). Nós com menor custo f têm maior prioridade.

        Args:
            other (NoFila): Outro nó para comparação.

        Returns:
            bool: True se o nó atual tiver menor custo f que o nó other, False caso contrário.
        """
        return self.custo_f < other.custo_f


class OtimizadorTriagemAStar:
    """
    Implementa o algoritmo A* para otimizar a ordem de atendimento dos pacientes na triagem, minimizando o risco global.
    """

    def __init__(self, tempo_atendimento_minutos: int = 15):
        self.tempo_atendimento = tempo_atendimento_minutos

    def calcular_risco_paciente(self, prob_alta: float, tempo_espera: int) -> float:
        return prob_alta * tempo_espera

    def otimizar_fila(self, pacientes: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        """
        Executa o A* usando uma Priority Queue (heapq nativo) para encontrar
        a ordem ideal de atendimento que minimiza o risco global.
        Retorna a lista ordenada de IDs e o risco total acumulado final.
        """
        # Nó inicial: todos os pacientes aguardam atendimento, tempo = 0
        no_inicial = NoFila(
            pacientes_restantes=pacientes,
            risco_acumulado_g=0.0,
            ordem_atendimento=[],
            tempo_atual=0,
        )

        fronteira: List[NoFila] = []
        heapq.heappush(fronteira, no_inicial)

        while fronteira:
            no_atual = heapq.heappop(fronteira)

            if not no_atual.pacientes_restantes:
                return no_atual.ordem_atendimento, no_atual.risco_acumulado_g

            for i, paciente in enumerate(no_atual.pacientes_restantes):
                tempo_espera_real = (
                    no_atual.tempo_atual + paciente["TempoEspera_Inicial_Minutos"]
                )
                risco_atendimento = self.calcular_risco_paciente(
                    paciente["Probabilidade_Alta"], tempo_espera_real
                )

                novo_risco_g = no_atual.risco_acumulado_g + risco_atendimento

                novos_restantes = no_atual.pacientes_restantes.copy()
                novos_restantes.pop(i)

                nova_ordem = no_atual.ordem_atendimento + [paciente["ID_Paciente"]]

                novo_tempo = no_atual.tempo_atual + self.tempo_atendimento

                novo_no = NoFila(novos_restantes, novo_risco_g, nova_ordem, novo_tempo)
                heapq.heappush(fronteira, novo_no)

        return [], 0.0
