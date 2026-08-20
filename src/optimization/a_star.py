import heapq
from typing import List, Tuple, Literal
from src import config
from src.optimization.risk import calcular_risco
from src.models.paciente import Paciente


class NoFila:
    def __init__(
        self,
        pacientes_restantes: List[Paciente],
        risco_acumulado_g: float,
        ordem_atendimento: List[int],
        tempo_atual: int,
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
    ):
        self.pacientes_restantes = pacientes_restantes
        self.risco_acumulado_g = risco_acumulado_g
        self.ordem_atendimento = ordem_atendimento
        self.tempo_atual = tempo_atual
        self.tipo_funcao = tipo_funcao

        self.heuristica_h = self.calcular_heuristica()
        self.custo_f = self.risco_acumulado_g + self.heuristica_h

    def calcular_heuristica(self) -> float:
        risco_h = 0.0
        for p in self.pacientes_restantes:
            tempo_espera_total = self.tempo_atual + p.tempo_espera_inicial_minutos
            risco_h += calcular_risco(
                p.probabilidade_alta, tempo_espera_total, self.tipo_funcao
            )
        return risco_h

    def __lt__(self, other: "NoFila") -> bool:
        return self.custo_f < other.custo_f


class OtimizadorTriagemAStar:
    def __init__(
        self, tempo_atendimento_minutos: int = config.TEMPO_ATENDIMENTO_MINUTOS
    ):
        self.tempo_atendimento = tempo_atendimento_minutos

    def calcular_risco_paciente(
        self,
        prob_alta: float,
        tempo_espera: int,
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
    ) -> float:
        return calcular_risco(prob_alta, tempo_espera, tipo_funcao)

    def otimizar_fila(
        self,
        pacientes: List[Paciente],
        tamanho_janela: int = config.TAMANHO_JANELA_A_STAR,
        tipo_funcao: Literal["linear", "exponencial"] = "linear",
        estrategia_particionamento: Literal["fifo", "risco_inicial"] = "fifo",
        usar_janela: bool = True,
    ) -> Tuple[List[int], float]:
        """
        Executa o A*. Se 'usar_janela' for False, o algoritmo atuará de forma global,
        processando a fila inteira em um único bloco matemático (restrito a filas pequenas).
        """
        janela_efetiva = tamanho_janela if usar_janela else len(pacientes)

        if estrategia_particionamento == "risco_inicial":
            pacientes_ordenados = sorted(
                pacientes,
                key=lambda x: self.calcular_risco_paciente(
                    x.probabilidade_alta,
                    x.tempo_espera_inicial_minutos,
                    tipo_funcao,
                ),
                reverse=True,
            )
        else:
            pacientes_ordenados = sorted(
                pacientes, key=lambda x: x.tempo_espera_inicial_minutos, reverse=True
            )

        ordem_final_global: List[int] = []
        risco_total_global = 0.0
        tempo_acumulado = 0

        for i in range(0, len(pacientes_ordenados), janela_efetiva):
            lote = [p.model_copy() for p in pacientes_ordenados[i : i + janela_efetiva]]

            no_inicial = NoFila(
                lote,
                risco_acumulado_g=0.0,
                ordem_atendimento=[],
                tempo_atual=tempo_acumulado,
                tipo_funcao=tipo_funcao,
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
                        no_atual.tempo_atual + paciente.tempo_espera_inicial_minutos
                    )
                    risco_atendimento = self.calcular_risco_paciente(
                        paciente.probabilidade_alta, tempo_espera_real, tipo_funcao
                    )

                    novo_risco_g = no_atual.risco_acumulado_g + risco_atendimento
                    novos_restantes = no_atual.pacientes_restantes.copy()
                    novos_restantes.pop(j)
                    nova_ordem = no_atual.ordem_atendimento + [paciente.id_paciente]
                    novo_tempo = no_atual.tempo_atual + self.tempo_atendimento

                    novo_no = NoFila(
                        novos_restantes,
                        novo_risco_g,
                        nova_ordem,
                        novo_tempo,
                        tipo_funcao,
                    )
                    heapq.heappush(fronteira, novo_no)

        return ordem_final_global, risco_total_global
