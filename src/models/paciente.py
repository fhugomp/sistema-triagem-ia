from typing import Literal, Dict
from pydantic import BaseModel, Field, ConfigDict


class Paciente(BaseModel):
    """Representação tipada e validada de um paciente no sistema de triagem."""
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    id_paciente: int = Field(alias="ID_Paciente", ge=1)
    idade_anos: int = Field(alias="Idade_Anos", ge=0, le=120)
    idade_avancada: Literal["Falso", "Verdadeiro"] = Field(alias="IdadeAvancada")
    doenca_cronica: Literal["Falso", "Verdadeiro"] = Field(alias="DoencaCronica")
    saturacao_o2: Literal["Normal", "Baixa"] = Field(alias="SaturacaoO2")
    frequencia_cardiaca: Literal["Normal", "Alta"] = Field(alias="FrequenciaCardiaca")
    nivel_dor: Literal["Leve", "Intensa"] = Field(alias="NivelDor")
    febre: Literal["Ausente", "Presente"] = Field(alias="Febre")
    tempo_espera_inicial_minutos: int = Field(alias="TempoEspera_Inicial_Minutos", ge=0)
    probabilidade_alta: float = Field(alias="Probabilidade_Alta", default=0.0, ge=0.0, le=1.0)

    @property
    def evidencias_bayesianas(self) -> Dict[str, str]:
        """Retorna os dados clínicos formatados como evidências para a Rede Bayesiana."""
        return {
            "IdadeAvancada": self.idade_avancada,
            "DoencaCronica": self.doenca_cronica,
            "SaturacaoO2": self.saturacao_o2,
            "FrequenciaCardiaca": self.frequencia_cardiaca,
            "NivelDor": self.nivel_dor,
            "Febre": self.febre,
        }
