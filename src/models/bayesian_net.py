from typing import Dict, cast, List, Union
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor
from pgmpy.inference import VariableElimination
from src import config
from src.models.paciente import Paciente


class SistemaTriagemBayesiana:
    """
    Sistema de triagem médica baseado numa Rede Bayesiana Diagnóstica.
    Estrutura com relacionamentos causais entre evidências -> Nó Central (Gravidade).
    """

    def __init__(self) -> None:
        self.model = BayesianNetwork(
            [
                ("IdadeAvancada", "DoencaCronica"),
                ("IdadeAvancada", "Gravidade"),
                ("DoencaCronica", "SaturacaoO2"),
                ("DoencaCronica", "Gravidade"),
                ("SaturacaoO2", "Gravidade"),
                ("Febre", "FrequenciaCardiaca"),
                ("FrequenciaCardiaca", "Gravidade"),
                ("NivelDor", "Gravidade"),
                ("Febre", "Gravidade"),
            ]
        )

        self._construir_cpts()
        self.model.check_model()
        self.inferencia = VariableElimination(self.model)
        self._cache_inferencia: Dict[str, Dict[str, float]] = {}

    def _construir_cpts(self) -> None:
        """
        Define as tabelas de probabilidade condicional.
        """
        # CPTs Independentes (Nós Raiz)
        cpd_idade = TabularCPD(
            "IdadeAvancada",
            2,
            [[0.7], [0.3]],
            state_names={"IdadeAvancada": ["Falso", "Verdadeiro"]},
        )
        cpd_dor = TabularCPD(
            "NivelDor", 2, [[0.6], [0.4]], state_names={"NivelDor": ["Leve", "Intensa"]}
        )
        cpd_febre = TabularCPD(
            "Febre", 2, [[0.75], [0.25]], state_names={"Febre": ["Ausente", "Presente"]}
        )

        # CPTs Condicionais
        # IdadeAvancada -> DoencaCronica
        # IdadeAvancada:   Falso  Verdadeiro
        # Falso            0.80   0.45
        # Verdadeiro       0.20   0.55
        cpd_doenca = TabularCPD(
            variable="DoencaCronica",
            variable_card=2,
            values=[[0.80, 0.45], [0.20, 0.55]],
            evidence=["IdadeAvancada"],
            evidence_card=[2],
            state_names={"DoencaCronica": ["Falso", "Verdadeiro"], "IdadeAvancada": ["Falso", "Verdadeiro"]},
        )

        # DoencaCronica -> SaturacaoO2
        # DoencaCronica:   Falso  Verdadeiro
        # Normal           0.90   0.70
        # Baixa            0.10   0.30
        cpd_sat = TabularCPD(
            variable="SaturacaoO2",
            variable_card=2,
            values=[[0.90, 0.70], [0.10, 0.30]],
            evidence=["DoencaCronica"],
            evidence_card=[2],
            state_names={"SaturacaoO2": ["Normal", "Baixa"], "DoencaCronica": ["Falso", "Verdadeiro"]},
        )

        # Febre -> FrequenciaCardiaca
        # Febre:           Ausente Presente
        # Normal           0.80    0.45
        # Alta             0.20    0.55
        cpd_freq = TabularCPD(
            variable="FrequenciaCardiaca",
            variable_card=2,
            values=[[0.80, 0.45], [0.20, 0.55]],
            evidence=["Febre"],
            evidence_card=[2],
            state_names={"FrequenciaCardiaca": ["Normal", "Alta"], "Febre": ["Ausente", "Presente"]},
        )

        # CPT Dinâmica para Gravidade (6 pais = 2^6 = 64 combinações)
        probs_baixa: List[float] = []
        probs_media: List[float] = []
        probs_alta: List[float] = []

        # Pgmpy itera a evidência da direita para a esquerda. Ordem: Febre, Dor, Freq, Sat, Doenca, Idade
        for i in range(64):
            idade = (i >> 5) & 1
            doenca = (i >> 4) & 1
            sat = (i >> 3) & 1
            freq = (i >> 2) & 1
            dor = (i >> 1) & 1
            febre = i & 1

            score = (
                (idade * 1.5)
                + (doenca * 2.0)
                + (sat * 3.5)
                + (freq * 1.0)
                + (dor * 1.5)
                + (febre * 1.0)
            )
            max_score = 10.5

            fator_risco = score / max_score

            if fator_risco < 0.3:
                p_alta = fator_risco * 0.1
                p_baixa = 0.8 - (fator_risco * 0.5)
            elif fator_risco < 0.7:
                p_alta = fator_risco * 0.5
                p_baixa = 0.4 - (fator_risco * 0.3)
            else:
                p_alta = min(0.95, fator_risco * 1.2)
                p_baixa = 0.01

            p_baixa = max(0.01, p_baixa)
            p_media = max(0.01, 1.0 - p_alta - p_baixa)

            soma = p_baixa + p_media + p_alta
            probs_baixa.append(p_baixa / soma)
            probs_media.append(p_media / soma)
            probs_alta.append(p_alta / soma)

        cpd_gravidade = TabularCPD(
            variable="Gravidade",
            variable_card=3,
            values=[probs_baixa, probs_media, probs_alta],
            evidence=[
                "IdadeAvancada",
                "DoencaCronica",
                "SaturacaoO2",
                "FrequenciaCardiaca",
                "NivelDor",
                "Febre",
            ],
            evidence_card=[2, 2, 2, 2, 2, 2],
            state_names={
                "Gravidade": config.ESTADOS_GRAVIDADE,
                "IdadeAvancada": ["Falso", "Verdadeiro"],
                "DoencaCronica": ["Falso", "Verdadeiro"],
                "SaturacaoO2": ["Normal", "Baixa"],
                "FrequenciaCardiaca": ["Normal", "Alta"],
                "NivelDor": ["Leve", "Intensa"],
                "Febre": ["Ausente", "Presente"],
            },
        )

        self.model.add_cpds(
            cpd_idade, cpd_doenca, cpd_sat, cpd_freq, cpd_dor, cpd_febre, cpd_gravidade
        )

    def calcular_probabilidade_gravidade(
        self, paciente_ou_evidencias: Union[Dict[str, str], Paciente]
    ) -> Dict[str, float]:
        if isinstance(paciente_ou_evidencias, Paciente):
            evidencias = paciente_ou_evidencias.evidencias_bayesianas
        else:
            evidencias = paciente_ou_evidencias

        chave_cache = "_".join(f"{k}-{v}" for k, v in sorted(evidencias.items()))
        if chave_cache in self._cache_inferencia:
            return self._cache_inferencia[chave_cache]

        resultado = cast(
            DiscreteFactor,
            self.inferencia.query(variables=["Gravidade"], evidence=evidencias),
        )

        probs = {
            config.ESTADOS_GRAVIDADE[0]: float(resultado.values[0]),
            config.ESTADOS_GRAVIDADE[1]: float(resultado.values[1]),
            config.ESTADOS_GRAVIDADE[2]: float(resultado.values[2]),
        }

        self._cache_inferencia[chave_cache] = probs
        return probs
