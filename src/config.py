"""
Módulo de configurações globais e constantes do Sistema Inteligente de Triagem.
Evita o uso de 'Magic Numbers' no código-fonte.
"""

# Parâmetros do Hospital / IA
TEMPO_ATENDIMENTO_MINUTOS = 15
SEED_DETERMINISTICA = 13
TAMANHO_JANELA_A_STAR = 8

# Parâmetros da Interface Web (Streamlit)
SLIDER_MIN_PACIENTES = 5
SLIDER_MAX_PACIENTES = 100
SLIDER_DEFAULT_PACIENTES = 8

# Constante de controle da Função Exponencial (Tau)
TAU_EXPONENCIAL = 60.0

# Distribuições de Probabilidade para Geração de Dados Sintéticos
DISTRIBUICAO_DOENCA_CRONICA = {"valores": ["Falso", "Verdadeiro"], "pesos": [0.70, 0.30]}
DISTRIBUICAO_SATURACAO_O2 = {"valores": ["Normal", "Baixa"], "pesos": [0.85, 0.15]}
DISTRIBUICAO_FREQ_CARDIACA = {"valores": ["Normal", "Alta"], "pesos": [0.70, 0.30]}
DISTRIBUICAO_DOR = {"valores": ["Leve", "Intensa"], "pesos": [0.60, 0.40]}
DISTRIBUICAO_FEBRE = {"valores": ["Ausente", "Presente"], "pesos": [0.75, 0.25]}

# Faixas de Geração de Dados
FAIXA_IDADE = (18, 91)              # [min, max) para integers
LIMIAR_IDADE_AVANCADA = 60          # Idade a partir da qual é "avançada"
FAIXA_TEMPO_ESPERA = (0, 180)       # [min, max) em minutos

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
