import pandas as pd
import numpy as np


class GeradorPacientesSinteticos:
    """Gerador de dados de pacientes sintéticos para testes e validação do sistema de triagem bayesiana."""

    def __init__(self, seed: int | None = 13) -> None:
        if seed is not None:
            np.random.seed(seed)

    def gerar_pacientes(self, num_pacientes: int = 50) -> pd.DataFrame:
        """Gera um DataFrame com dados sintéticos de pacientes, incluindo variáveis relevantes para a triagem médica,

        Args:
            num_pacientes (int, optional): Número de pacientes a serem gerados. Defaults to 50.

        Returns:
            pd.DataFrame: DataFrame com os dados sintéticos dos pacientes.
        """
        idades = np.random.randint(18, 91, size=num_pacientes)
        idade_avancada = np.where(idades > 60, "Verdadeiro", "Falso")

        sat_o2 = np.random.choice(
            ["Normal", "Baixa"], size=num_pacientes, p=[0.85, 0.15]
        )
        freq_card = np.random.choice(
            ["Normal", "Alta"], size=num_pacientes, p=[0.70, 0.30]
        )
        dor = np.random.choice(["Leve", "Intensa"], size=num_pacientes, p=[0.60, 0.40])
        febre = np.random.choice(
            ["Ausente", "Presente"], size=num_pacientes, p=[0.75, 0.25]
        )

        tempos_espera_minutos = np.random.randint(0, 180, size=num_pacientes)

        df_pacientes = pd.DataFrame(
            {
                "ID_Paciente": np.arange(1, num_pacientes + 1),
                "Idade_Anos": idades,
                "IdadeAvancada": idade_avancada,
                "SaturacaoO2": sat_o2,
                "FrequenciaCardiaca": freq_card,
                "NivelDor": dor,
                "Febre": febre,
                "TempoEspera_Inicial_Minutos": tempos_espera_minutos,
            }
        )

        return df_pacientes
