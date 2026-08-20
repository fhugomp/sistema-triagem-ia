"""
Módulo puro de cálculo de risco clínico.
Centraliza a função de deterioração utilizada por todos os algoritmos de escalonamento.
"""

import math
from typing import Literal
from src import config


def calcular_risco(
    prob_alta: float,
    tempo_espera: int,
    tipo_funcao: Literal["linear", "exponencial"] = "linear",
) -> float:
    """Calcula o risco individual de um paciente: Risco = P(Alta) * f(t).

    Args:
        prob_alta: Probabilidade de gravidade alta estimada pela Rede Bayesiana.
        tempo_espera: Tempo total de espera do paciente em minutos.
        tipo_funcao: Modelo de deterioração clínica (linear ou exponencial).

    Returns:
        Valor escalar do risco clínico do paciente.
    """
    if tipo_funcao == "exponencial":
        return prob_alta * math.exp(tempo_espera / config.TAU_EXPONENCIAL)
    return prob_alta * tempo_espera
