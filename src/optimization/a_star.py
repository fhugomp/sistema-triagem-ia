import heapq
from typing import List, Tuple, Dict, Any
from src import config


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
        Calcula a heurística (h) para o nó atual.

        Foi utilizada uma heurística baseada na soma dos riscos atuais dos pacientes
        restantes, conforme sugerido pelo escopo do edital.
        """
        risco_h = 0.0
        for p in self.pacientes_restantes:
            tempo_espera_total = self.tempo_atual + p["TempoEspera_Inicial_Minutos"]
            risco_h += p["Probabilidade_Alta"] * tempo_espera_total
        return risco_h

    def __lt__(self, other: "NoFila") -> bool:
        """
        Método de comparação para a fila de prioridade, baseado no custo f (g + h).
        """
        return self.custo_f < other.custo_f


class OtimizadorTriagemAStar:
    """
    Implementa o algoritmo A* para otimizar a ordem de atendimento dos pacientes na triagem.
    """

    def __init__(
        self, tempo_atendimento_minutos: int = config.TEMPO_ATENDIMENTO_MINUTOS
    ):
        self.tempo_atendimento = tempo_atendimento_minutos

    def calcular_risco_paciente(self, prob_alta: float, tempo_espera: int) -> float:
        """
        Calcula o risco individual de deterioração clínica.
        """
        return prob_alta * tempo_espera

    def otimizar_fila(
        self,
        pacientes: List[Dict[str, Any]],
        tamanho_janela: int = config.TAMANHO_JANELA_A_STAR,
    ) -> Tuple[List[int], float]:
        """
        Executa o algoritmo A* através de um particionamento da fila (Sliding Window)
        para contornar a explosão combinatória $O(N!)$.

        ATENÇÃO ACADÊMICA:
        Esta abordagem sacrifica a garantia matemática do ótimo global. O algoritmo
        encontra uma ordem localmente ótima dentro de cada lote.

        Como a base sintética não possui timestamp explícito de chegada, o tempo de
        espera inicial foi utilizado como aproximação da ordem FIFO para a pré-ordenação
        dos lotes, garantindo que pacientes antigos sejam processados primeiro.
        """
        pacientes_ordenados = sorted(
            pacientes, key=lambda x: x["TempoEspera_Inicial_Minutos"], reverse=True
        )

        ordem_final_global: List[int] = []
        risco_total_global = 0.0
        tempo_acumulado = 0

        for i in range(0, len(pacientes_ordenados), tamanho_janela):
            # Criação de cópias defensivas para eliminar efeitos colaterais
            lote = [p.copy() for p in pacientes_ordenados[i : i + tamanho_janela]]

            for p in lote:
                p["TempoEspera_Inicial_Minutos"] += tempo_acumulado

            no_inicial = NoFila(
                lote,
                risco_acumulado_g=0.0,
                ordem_atendimento=[],
                tempo_atual=tempo_acumulado,
            )
            fronteira: List[NoFila] = []
            heapq.heappush(fronteira, no_inicial)

            while fronteira:
                no_atual = heapq.heappop(fronteira)

                if not no_atual.pacientes_restantes:
                    ordem_final_global.extend(no_atual.ordem_atendimento)
                    risco_total_global += no_atual.risco_acumulado_g
                    tempo_acumulado = no_atual.tempo_atual
                    break

                for j, paciente in enumerate(no_atual.pacientes_restantes):
                    tempo_espera_real = (
                        no_atual.tempo_atual + paciente["TempoEspera_Inicial_Minutos"]
                    )
                    risco_atendimento = self.calcular_risco_paciente(
                        paciente["Probabilidade_Alta"], tempo_espera_real
                    )

                    novo_risco_g = no_atual.risco_acumulado_g + risco_atendimento
                    novos_restantes = no_atual.pacientes_restantes.copy()
                    novos_restantes.pop(j)
                    nova_ordem = no_atual.ordem_atendimento + [paciente["ID_Paciente"]]
                    novo_tempo = no_atual.tempo_atual + self.tempo_atendimento

                    novo_no = NoFila(
                        novos_restantes, novo_risco_g, nova_ordem, novo_tempo
                    )
                    heapq.heappush(fronteira, novo_no)

        return ordem_final_global, risco_total_global
