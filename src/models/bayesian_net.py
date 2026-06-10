from typing import Dict, cast
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor
from pgmpy.inference import VariableElimination
from src import config


class SistemaTriagemBayesiana:
    """Sistema de triagem médica baseado em um modelo de rede bayesiana.
    O modelo é construído com base em variáveis como:
    "Idade Avançada", "Gravidade", "Saturação de O2",
    "Frequência Cardíaca", "Nível de Dor", "Febre".
    """

    def __init__(self) -> None:
        self.model = BayesianNetwork(
            [
                ("IdadeAvancada", "Gravidade"),
                ("DoencaCronica", "Gravidade"),
                ("Gravidade", "SaturacaoO2"),
                ("Gravidade", "FrequenciaCardiaca"),
                ("Gravidade", "NivelDor"),
                ("Gravidade", "Febre"),
            ]
        )

        self._construir_cpts()
        # Modelo validado estritamente pelo pgmpy
        self.model.check_model()
        self.inferencia = VariableElimination(self.model)
        self._cache_inferencia: Dict[str, Dict[str, float]] = {}

    def _construir_cpts(self) -> None:
        """Define as tabelas de probabilidade condicional (CPTs) para cada variável."""
        cpd_idade = TabularCPD(
            variable="IdadeAvancada",
            variable_card=2,
            values=[[0.7], [0.3]],
            state_names={"IdadeAvancada": ["Falso", "Verdadeiro"]},
        )

        cpd_doenca_cronica = TabularCPD(
            variable="DoencaCronica",
            variable_card=2,
            values=[[0.7], [0.3]],
            state_names={"DoencaCronica": ["Falso", "Verdadeiro"]},
        )

        cpd_gravidade = TabularCPD(
            variable="Gravidade",
            variable_card=3,
            values=[
                [0.80, 0.50, 0.40, 0.10],  # Probabilidade de Gravidade = baixa
                [0.15, 0.30, 0.40, 0.30],  # Probabilidade de Gravidade = média
                [0.05, 0.20, 0.20, 0.60],  # Probabilidade de Gravidade = alta
            ],
            evidence=["IdadeAvancada", "DoencaCronica"],
            evidence_card=[2, 2],
            state_names={
                "Gravidade": config.ESTADOS_GRAVIDADE,
                "IdadeAvancada": ["Falso", "Verdadeiro"],
                "DoencaCronica": ["Falso", "Verdadeiro"],
            },
        )

        cpd_saturacao = TabularCPD(
            variable="SaturacaoO2",
            variable_card=2,
            values=[
                [0.95, 0.70, 0.10],  # Normal
                [0.05, 0.30, 0.90],  # Baixa
            ],
            evidence=["Gravidade"],
            evidence_card=[3],
            state_names={
                "SaturacaoO2": ["Normal", "Baixa"],
                "Gravidade": config.ESTADOS_GRAVIDADE,
            },
        )

        cpd_frequencia = TabularCPD(
            variable="FrequenciaCardiaca",
            variable_card=2,
            values=[
                [0.90, 0.50, 0.20],  # Normal
                [0.10, 0.50, 0.80],  # Alta(Taquicardia)
            ],
            evidence=["Gravidade"],
            evidence_card=[3],
            state_names={
                "FrequenciaCardiaca": ["Normal", "Alta"],
                "Gravidade": config.ESTADOS_GRAVIDADE,
            },
        )

        cpd_nivel_dor = TabularCPD(
            variable="NivelDor",
            variable_card=2,
            values=[
                [0.80, 0.40, 0.15],  # Leve
                [0.20, 0.60, 0.85],  # Intensa
            ],
            evidence=["Gravidade"],
            evidence_card=[3],
            state_names={
                "NivelDor": ["Leve", "Intensa"],
                "Gravidade": config.ESTADOS_GRAVIDADE,
            },
        )

        cpd_febre = TabularCPD(
            variable="Febre",
            variable_card=2,
            values=[
                [0.85, 0.50, 0.30],  # Ausente
                [0.15, 0.50, 0.70],  # Presente
            ],
            evidence=["Gravidade"],
            evidence_card=[3],
            state_names={
                "Febre": ["Ausente", "Presente"],
                "Gravidade": config.ESTADOS_GRAVIDADE,
            },
        )

        self.model.add_cpds(
            cpd_idade,
            cpd_doenca_cronica,
            cpd_gravidade,
            cpd_saturacao,
            cpd_frequencia,
            cpd_nivel_dor,
            cpd_febre,
        )

    def calcular_probabilidade_gravidade(
        self, evidencias: Dict[str, str]
    ) -> Dict[str, float]:
        """
        Calcula a probabilidade de cada nível de gravidade.
        """
        chave_cache = "_".join(f"{k}-{v}" for k, v in sorted(evidencias.items()))

        if chave_cache in self._cache_inferencia:
            return self._cache_inferencia[chave_cache]

        resultado = cast(
            DiscreteFactor,
            self.inferencia.query(variables=["Gravidade"], evidence=evidencias),
        )

        # Utilizando os estados do config para blindar o dicionário de saída
        probs = {
            config.ESTADOS_GRAVIDADE[0]: float(resultado.values[0]),
            config.ESTADOS_GRAVIDADE[1]: float(resultado.values[1]),
            config.ESTADOS_GRAVIDADE[2]: float(resultado.values[2]),
        }

        self._cache_inferencia[chave_cache] = probs
        return probs
