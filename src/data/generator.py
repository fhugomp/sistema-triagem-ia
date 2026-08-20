import pandas as pd
import numpy as np
from typing import List, cast, Literal
from src import config
from src.models.paciente import Paciente


class GeradorPacientesSinteticos:
    """Gerador de dados de pacientes sintéticos para testes e validação do sistema de triagem bayesiana."""

    def __init__(self, seed: int | None = config.SEED_DETERMINISTICA) -> None:
        self.rng = np.random.default_rng(seed)

    def gerar_pacientes(self, num_pacientes: int = 50) -> List[Paciente]:
        """Gera uma lista de pacientes sintéticos, incluindo variáveis relevantes para a triagem médica.

        Args:
            num_pacientes (int, optional): Número de pacientes a serem gerados. Defaults to 50.

        Returns:
            List[Paciente]: Lista com os dados sintéticos dos pacientes validados pelo modelo.
        """
        idades = self.rng.integers(config.FAIXA_IDADE[0], config.FAIXA_IDADE[1], size=num_pacientes)
        idade_avancada = np.where(idades >= config.LIMIAR_IDADE_AVANCADA, "Verdadeiro", "Falso")
        doenca_cronica = self.rng.choice(
            config.DISTRIBUICAO_DOENCA_CRONICA["valores"],
            size=num_pacientes,
            p=config.DISTRIBUICAO_DOENCA_CRONICA["pesos"]
        )

        sat_o2 = self.rng.choice(
            config.DISTRIBUICAO_SATURACAO_O2["valores"],
            size=num_pacientes,
            p=config.DISTRIBUICAO_SATURACAO_O2["pesos"]
        )
        freq_card = self.rng.choice(
            config.DISTRIBUICAO_FREQ_CARDIACA["valores"],
            size=num_pacientes,
            p=config.DISTRIBUICAO_FREQ_CARDIACA["pesos"]
        )
        dor = self.rng.choice(
            config.DISTRIBUICAO_DOR["valores"],
            size=num_pacientes,
            p=config.DISTRIBUICAO_DOR["pesos"]
        )
        febre = self.rng.choice(
            config.DISTRIBUICAO_FEBRE["valores"],
            size=num_pacientes,
            p=config.DISTRIBUICAO_FEBRE["pesos"]
        )

        tempos_espera_minutos = self.rng.integers(config.FAIXA_TEMPO_ESPERA[0], config.FAIXA_TEMPO_ESPERA[1], size=num_pacientes)

        pacientes = []
        for i in range(num_pacientes):
            p = Paciente(
                id_paciente=i + 1,
                idade_anos=int(idades[i]),
                idade_avancada=cast(Literal["Falso", "Verdadeiro"], idade_avancada[i]),
                doenca_cronica=cast(Literal["Falso", "Verdadeiro"], doenca_cronica[i]),
                saturacao_o2=cast(Literal["Normal", "Baixa"], sat_o2[i]),
                frequencia_cardiaca=cast(Literal["Normal", "Alta"], freq_card[i]),
                nivel_dor=cast(Literal["Leve", "Intensa"], dor[i]),
                febre=cast(Literal["Ausente", "Presente"], febre[i]),
                tempo_espera_inicial_minutos=int(tempos_espera_minutos[i]),
            )
            pacientes.append(p)

        return pacientes
