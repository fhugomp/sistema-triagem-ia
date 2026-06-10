"""
Módulo de configurações globais e constantes do Sistema Inteligente de Triagem.
Evita o uso de 'Magic Numbers' no código-fonte.
"""

# Parâmetros do Hospital / IA
TEMPO_ATENDIMENTO_MINUTOS = 15
SEED_DETERMINISTICA = 13
TAMANHO_JANELA_A_STAR = 8

# Parâmetros da Interface Web (Streamlit)
SLIDER_MIN_PACIENTES = 10
SLIDER_MAX_PACIENTES = 100
SLIDER_DEFAULT_PACIENTES = 30

# Nomenclatura Padrão de Variáveis da Rede Bayesiana
VARIAVEIS_ENTRADA = [
    "IdadeAvancada",
    "DoencaCronica",
    "SaturacaoO2",
    "FrequenciaCardiaca",
    "NivelDor",
    "Febre",
]

ESTADOS_GRAVIDADE = ["baixa", "média", "alta"]
