from typing import Dict, cast, List
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor
from pgmpy.inference import VariableElimination
from src import config


class SistemaTriagemBayesiana:
    """
    Sistema de triagem médica baseado numa Rede Bayesiana Diagnóstica.
    Estrutura aderente ao edital: Evidências (Sintomas) -> Nó Central (Gravidade).
    """

    def __init__(self) -> None:
        self.model = BayesianNetwork(
            [
                ("IdadeAvancada", "Gravidade"),
                ("DoencaCronica", "Gravidade"),
                ("SaturacaoO2", "Gravidade"),
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
        Como a Gravidade depende de 6 nós pais, a sua CPT possui 64 colunas.
        """
        # CPTs Independentes (Nós Raiz)
        cpd_idade = TabularCPD(
            "IdadeAvancada",
            2,
            [[0.7], [0.3]],
            state_names={"IdadeAvancada": ["Falso", "Verdadeiro"]},
        )
        cpd_doenca = TabularCPD(
            "DoencaCronica",
            2,
            [[0.7], [0.3]],
            state_names={"DoencaCronica": ["Falso", "Verdadeiro"]},
        )
        cpd_sat = TabularCPD(
            "SaturacaoO2",
            2,
            [[0.85], [0.15]],
            state_names={"SaturacaoO2": ["Normal", "Baixa"]},
        )
        cpd_freq = TabularCPD(
            "FrequenciaCardiaca",
            2,
            [[0.7], [0.3]],
            state_names={"FrequenciaCardiaca": ["Normal", "Alta"]},
        )
        cpd_dor = TabularCPD(
            "NivelDor", 2, [[0.6], [0.4]], state_names={"NivelDor": ["Leve", "Intensa"]}
        )
        cpd_febre = TabularCPD(
            "Febre", 2, [[0.75], [0.25]], state_names={"Febre": ["Ausente", "Presente"]}
        )

        # CPT Dinâmica para Gravidade (6 pais = 2^6 = 64 combinações)
        # Utilizaremos um sistema de pontuação para preencher a tabela de forma clinicamente plausível
        probs_baixa: List[float] = []
        probs_media: List[float] = []
        probs_alta: List[float] = []

        # Pgmpy itera a evidência da direita para a esquerda. Ordem: Febre, Dor, Freq, Sat, Doenca, Idade
        for i in range(64):
            # Converte o índice i para binário para saber os estados (0=Falso/Normal, 1=Verdadeiro/Anormal)
            idade = (i >> 5) & 1
            doenca = (i >> 4) & 1
            sat = (i >> 3) & 1
            freq = (i >> 2) & 1
            dor = (i >> 1) & 1
            febre = i & 1

            # Score Clínico Baseado em Pesos
            score = (
                (idade * 1.5)
                + (doenca * 2.0)
                + (sat * 3.5)
                + (freq * 1.0)
                + (dor * 1.5)
                + (febre * 1.0)
            )
            max_score = 10.5  # Soma de todos os pesos

            fator_risco = score / max_score

            # Distribuição heurística baseada no fator de risco
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

            # Normalização estrita para fechar em 1.0
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
        self, evidencias: Dict[str, str]
    ) -> Dict[str, float]:
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
