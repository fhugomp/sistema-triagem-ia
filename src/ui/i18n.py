"""
Modulo de internacionalizacao (i18n) — suporte PT-BR / EN.
Centraliza todos os textos da interface em um dicionario unico.
"""


from typing import Dict, Any


# ---------------------------------------------------------------------------
# Node label translations for the Bayesian Network graph
# ---------------------------------------------------------------------------

NODE_LABELS: Dict[str, Dict[str, str]] = {
    "pt": {
        "IdadeAvancada":      "IdadeAvancada",
        "DoencaCronica":      "DoencaCronica",
        "SaturacaoO2":        "SaturacaoO2",
        "FrequenciaCardiaca": "FrequenciaCardiaca",
        "NivelDor":           "NivelDor",
        "Febre":              "Febre",
        "Gravidade":          "Gravidade",
    },
    "en": {
        "IdadeAvancada":      "AdvancedAge",
        "DoencaCronica":      "ChronicDisease",
        "SaturacaoO2":        "O2Saturation",
        "FrequenciaCardiaca": "HeartRate",
        "NivelDor":           "PainLevel",
        "Febre":              "Fever",
        "Gravidade":          "Severity",
    },
}


# ---------------------------------------------------------------------------
# Main translation dictionary
# ---------------------------------------------------------------------------

TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    "pt": {
        # --- Branding ---
        "brand_tagline": "Intelligent Clinical Queue Optimization",
        "hero_title": "Otimizacao Inteligente\nde Filas Clinicas",
        "hero_cta": "Iniciar Simulacao",

        # --- Navbar ---
        "nav_overview":    "Overview",
        "nav_simulation":  "Simulation",
        "nav_methodology": "Methodology",
        "nav_hint": "Navegue pelos modulos na barra de navegacao.",

        # --- Highlights (stats pills) ---
        "hl_nodes": "NOS DA REDE",
        "hl_arcs":  "ARCOS CAUSAIS",
        "hl_cpt":   "COMBINACOES CPT",
        "hl_manch": "CATEGORIAS MANCHESTER",
        "hl_risk_reduction": "Reducao de risco acumulado global vs Heuristica Gulosa sob penalidade exponencial",
        "nav_info_extra": (
            " — **Simulation**: execute cenarios e visualize a otimizacao em tempo real. "
            "**Methodology**: grafo causal interativo e embasamento matematico."
        ),

        # --- Overview (main.py) ---
        "overview_hero_sub": (
            "Plataforma experimental para minimizacao de risco clinico em "
            "prontos-socorros operando sob incerteza probabilistica."
        ),
        "overview_arch_header": "Arquitetura do Sistema",

        # Module cards
        "mod_01_num":   "01. INFERENCIA BAYESIANA",
        "mod_01_title": "Modelagem de Incerteza",
        "mod_01_desc": (
            "Rede Bayesiana Diagnostica com 7 nos e 9 arcos causais. "
            "Inferencia exata por Variable Elimination com memoization — "
            "acesso O(1) para consultas repetidas."
        ),
        "mod_02_num":   "02. MODELAGEM DE RISCO",
        "mod_02_title": "Penalidade Temporal",
        "mod_02_desc": (
            "Funcoes de custo linear e exponencial que quantificam a deterioracao "
            "clinica progressiva em funcao do tempo de espera do paciente."
        ),
        "mod_03_num":   "03. OTIMIZACAO A*",
        "mod_03_title": "Busca Heuristica",
        "mod_03_desc": (
            "Motor de busca que minimiza o risco clinico acumulado global. "
            "Modo global (N <= 8) e Sliding Window — complexidade reduzida de "
            "O(N!) para O(ceil(N/k)*k!)."
        ),

        # --- Simulation ---
        "sim_title":             "Simulation",
        "sim_subtitle":          "Configure o experimento e execute o pipeline completo de triagem.",
        "sim_setup_header":      "EXPERIMENT SETUP",
        "sim_num_patients_label": "Tamanho da Amostra (Pacientes)",
        "sim_risk_fn_label":     "Funcao de Risco",
        "sim_risk_linear":       "Linear",
        "sim_risk_exp":          "Exponencial",
        "sim_mode_label":        "Modo do Algoritmo A*",
        "sim_mode_global":       "A* Global (Otimo Matematico)",
        "sim_mode_part":         "A* Particionado (Sliding Window)",
        "sim_btn":               "EXECUTAR SIMULACAO",
        "sim_block_error": (
            "Acao Bloqueada: o A* Global possui complexidade O(N!). "
            "Para N > 8 o processamento travaria. Reduza para 8 pacientes ou "
            "selecione o modo A* Particionado."
        ),
        "sim_initializing":  "Inicializando pipeline...",
        "sim_progress_text": "Processando lote {current} de {total}...",
        "sim_nodes_label":   "Nos explorados ate agora: {n}",
        "sim_completed":     "Concluido.",
        "sim_queue_header":  "OPTIMAL QUEUE  —  A* OUTPUT",
        "sim_report_header": "PERFORMANCE REPORT",
        "sim_audit_header":  "AUDITORIA DE FILA",
        "sim_audit_info": (
            "Exporte a ordem de atendimento ou inspecione as matrizes de "
            "permutacao por algoritmo."
        ),
        "sim_download_btn": "Baixar Dados A* (CSV)",
        "sim_audit_astar":  "Matriz de Permutacao: Busca A*",
        "sim_audit_greedy": "Matriz de Permutacao: Heuristica Gulosa",
        "sim_audit_fifo":   "Matriz de Permutacao: Aproximacao FIFO",

        # KPIs
        "kpi_exec_time":       "Tempo de Execucao",
        "kpi_exec_help":       "Wall-clock do pipeline completo: geracao + inferencia + otimizacao.",
        "kpi_nodes":           "Nos Explorados (A*)",
        "kpi_nodes_help":      "Soma das expansoes do heap em todos os lotes processados.",
        "kpi_wait_fifo":       "Espera Media - FIFO",
        "kpi_wait_fifo_help":  "Tempo medio de espera acumulado por paciente no FIFO.",
        "kpi_wait_astar":      "Espera Media - A*",
        "kpi_wait_astar_help": "Tempo medio de espera acumulado por paciente no A*.",

        # Charts
        "chart_risk_title":    "Risco Global Acumulado — Comparativo de Estrategias",
        "chart_profile_title": "Perfil Clinico — Protocolo de Manchester",
        "chart_x_risk":        "Risco Numerico",
        "chart_y_patients":    "Volume de Pacientes",
        "chart_fifo":          "FIFO",
        "chart_greedy":        "Gulosa",
        "chart_astar":         "A* (Otimizador)",

        # Metrics
        "metric_fifo":        "Risco Acumulado - FIFO",
        "metric_greedy":      "Risco Acumulado - Gulosa",
        "metric_astar":       "Risco Acumulado - A*",
        "metric_delta_label": "vs Gulosa",

        # Patient cards
        "card_prefix":    "PAC",
        "card_risk_high": "ALTO",
        "card_risk_med":  "MED",
        "card_risk_low":  "BAIXO",

        # Manchester display names
        "manch_nao_urgente":   "Nao Urgente",
        "manch_pouco_urgente": "Pouco Urgente",
        "manch_urgente":       "Urgente",
        "manch_muito_urgente": "Muito Urgente",
        "manch_emergencia":    "Emergencia",

        # Methodology — base
        "method_title":    "Methodology",
        "method_subtitle": "Fundamentacao teorica, modelagem causal e protocolo de triagem.",

        # Methodology — Bayesian Network
        "method_bn_header": "Rede Bayesiana Diagnostica",
        "method_bn_desc": (
            "A rede encapsula o conhecimento clinico sobre a relacao entre fatores de "
            "risco e a gravidade do quadro do paciente. Cada no representa uma variavel "
            "clinica binaria; cada arco representa uma dependencia causal direta."
        ),
        "method_graph_title": "Grafo Causal",
        "method_arcs_header": "Relacoes Causais",
        "method_arc_from":    "No de Origem",
        "method_arc_to":      "No de Destino",
        "method_arc_meaning": "Interpretacao Clinica",

        # Methodology — metrics
        "method_metrics_header": "Metricas Estruturais do Grafo",
        "method_metric_nodes":   "Total de Nos",
        "method_metric_arcs":    "Total de Arcos",
        "method_metric_roots":   "Nos Raiz",
        "method_metric_cpt":     "Combinacoes CPT",

        # Methodology — legends
        "method_legend_root":   "Nos Raiz — sem pais: IdadeAvancada, Febre, NivelDor",
        "method_legend_inter":  "Nos Intermediarios — DoencaCronica, SaturacaoO2, FrequenciaCardiaca",
        "method_legend_target": "No Alvo — Gravidade (3 estados: baixa, media, alta)",

        # Methodology — Variable Elimination
        "method_ve_header": "Inferencia Exata — Variable Elimination",
        "method_ve_body": (
            "A inferencia probabilistica e realizada pelo algoritmo exato de *Variable "
            "Elimination* (VE), que calcula a distribuicao marginal do no-alvo "
            "`Gravidade` condicionada as evidencias observadas, eliminando "
            "iterativamente as variaveis latentes via multiplicacao e marginalizacao "
            "de fatores. O resultado e um vetor de probabilidades `{baixa, media, alta}` "
            "normalizadas. Uma camada de **memoization** por hash SHA-256 das evidencias "
            "armazena resultados computados anteriormente, reduzindo inferencias repetidas "
            "de $O(2^n)$ para $O(1)$ amortizado — critica para a latencia em simulacoes "
            "de alta carga."
        ),

        # Methodology — Complexity
        "method_complexity_header": "Complexidade Computacional e Mitigacao",
        "method_complexity_body": (
            "O espaco de estados da fila de triagem cresce **fatorialmente** com o "
            "numero de pacientes $N$: uma enumeracao exaustiva teria complexidade "
            "$\\mathcal{O}(N!)$, inviabilizando filas com $N > 10$. O modulo implementa "
            "uma estrategia de **Sliding Window** (janela deslizante) com tamanho $k = 8$: "
            "a fila e particionada em $\\lceil N/k \\rceil$ lotes e o A* e aplicado "
            "localmente em cada lote, reduzindo a complexidade efetiva para "
            "$\\mathcal{O}(\\lceil N/k \\rceil \\times k!)$. Uma **heuristica de "
            "particionamento por risco inicial** ordena os lotes pela probabilidade de "
            "gravidade, mitigando a 'miopia de lote' e preservando a qualidade global "
            "da solucao."
        ),

        # Methodology — Cost functions
        "method_math_header": "Funcoes de Custo",
        "method_math_desc":   "O motor A* parametriza duas funcoes de deterioracao clinica:",
        "method_table_range": "Faixa de Probabilidade",
        "method_table_cat":   "Categoria",
        "method_table_color": "Cor",

        # Methodology — Empirical
        "method_empirical_header": "Resultados Empiricos",
        "method_empirical_body": (
            "Experimentos em cenarios de superlotacao ($N = 100$ pacientes) "
            "demonstraram que, sob **penalidade exponencial** ($\\tau = 60$ min), "
            "a estrategia A* Particionado supera a Heuristica Gulosa em mais de "
            "**50% de reducao de risco acumulado global**. Sob funcao linear, "
            "a diferenca e marginal, indicando que a vantagem do A* e mais pronunciada "
            "em cenarios de alta criticidade com deterioracao nao-linear."
        ),

        # Methodology — Manchester
        "method_manchester_header": "Protocolo de Manchester — Mapeamento de Categorias",
        "method_manchester_desc": (
            "Mapeamento da probabilidade continua de gravidade alta $[0, 1]$ para cinco "
            "categorias clinicas com limiares uniformes $\\Delta = 0{,}20$."
        ),

        # Methodology — Conclusions
        "method_conclusions_header": "Conclusoes da Pesquisa & Impacto",
        "method_conclusion_1_title": "Validade da Arquitetura Hibrida",
        "method_conclusion_1_body": (
            "A integracao de IA Simbolica (Rede Bayesiana para inferencia causal sob "
            "incerteza) com Pesquisa Operacional (busca A* para otimizacao combinatoria) "
            "provou-se arquiteturalmente solida. Cada componente e isolado por interfaces "
            "tipadas Pydantic, garantindo imutabilidade e testabilidade independente. "
            "A separacao de responsabilidades — inferencia, funcao de risco, otimizacao "
            "e renderizacao — permite substituicao de qualquer modulo sem regressao."
        ),
        "method_conclusion_2_title": "Superioridade do A* sob Penalidade Exponencial",
        "method_conclusion_2_body": (
            "Os experimentos confirmam a hipotese central: algoritmos gulosos sao "
            "suficientes para funcoes de custo linear (complexidade temporal de O(N log N)), "
            "mas falham sistematicamente em cenarios de alta criticidade com penalidade "
            "exponencial. O A* Particionado demonstrou reducao de risco superior a 50% "
            "nestes cenarios, validando a necessidade de exploracao heuristica do espaco "
            "de estados para contextos clinicos de alta urgencia."
        ),
        "method_conclusion_3_title": "Implicacoes Praticas e Trabalhos Futuros",
        "method_conclusion_3_body": (
            "O sistema constitui um ambiente de simulacao e validacao de algoritmos de "
            "escalonamento sob incerteza clinica. Para adocao em ambiente hospitalar real, "
            "trabalhos futuros devem incluir: (1) calibracao das CPTs com dados clinicos "
            "reais; (2) avaliacao da funcao de risco com especialistas medicos; "
            "(3) integracao com sistemas de prontuario eletronico (PEP); e "
            "(4) avaliacao de fairness para detectar possiveis vies nos dados sinteticos."
        ),

        # Footer
        "footer_by":        "Desenvolvido por Hugo Mendes",
        "footer_github":    "GitHub",
        "footer_linkedin":  "LinkedIn",
        "footer_portfolio": "Portfolio",
    },

    "en": {
        # --- Branding ---
        "brand_tagline": "Intelligent Clinical Queue Optimization",
        "hero_title": "Intelligent Clinical\nQueue Optimization",
        "hero_cta": "Start Simulation",

        # --- Navbar ---
        "nav_overview":    "Overview",
        "nav_simulation":  "Simulation",
        "nav_methodology": "Methodology",
        "nav_hint": "Navigate through modules in the top navigation bar.",

        # --- Highlights (stats pills) ---
        "hl_nodes": "NETWORK NODES",
        "hl_arcs":  "CAUSAL ARCS",
        "hl_cpt":   "CPT COMBINATIONS",
        "hl_manch": "MANCHESTER CATEGORIES",
        "hl_risk_reduction": "Global accumulated risk reduction vs Greedy Heuristic under exponential penalty",
        "nav_info_extra": (
            " — **Simulation**: run scenarios and visualize real-time optimization. "
            "**Methodology**: interactive causal graph and mathematical foundation."
        ),

        # --- Overview ---
        "overview_hero_sub": (
            "Experimental platform for clinical risk minimization in emergency "
            "departments operating under probabilistic uncertainty."
        ),
        "overview_arch_header": "System Architecture",

        # Module cards
        "mod_01_num":   "01. BAYESIAN INFERENCE",
        "mod_01_title": "Uncertainty Modeling",
        "mod_01_desc": (
            "Diagnostic Bayesian Network with 7 nodes and 9 causal arcs. "
            "Exact inference via Variable Elimination with memoization — "
            "O(1) access for repeated queries."
        ),
        "mod_02_num":   "02. RISK MODELING",
        "mod_02_title": "Temporal Penalty",
        "mod_02_desc": (
            "Linear and exponential cost functions quantifying progressive clinical "
            "deterioration as a function of patient waiting time."
        ),
        "mod_03_num":   "03. A* OPTIMIZATION",
        "mod_03_title": "Heuristic Search",
        "mod_03_desc": (
            "Search engine minimizing global accumulated clinical risk. "
            "Global mode (N <= 8) and Sliding Window — complexity reduced from "
            "O(N!) to O(ceil(N/k)*k!)."
        ),

        # --- Simulation ---
        "sim_title":             "Simulation",
        "sim_subtitle":          "Configure the experiment and run the complete triage pipeline.",
        "sim_setup_header":      "EXPERIMENT SETUP",
        "sim_num_patients_label": "Sample Size (Patients)",
        "sim_risk_fn_label":     "Risk Function",
        "sim_risk_linear":       "Linear",
        "sim_risk_exp":          "Exponential",
        "sim_mode_label":        "A* Algorithm Mode",
        "sim_mode_global":       "Global A* (Mathematical Optimum)",
        "sim_mode_part":         "Partitioned A* (Sliding Window)",
        "sim_btn":               "RUN SIMULATION",
        "sim_block_error": (
            "Blocked: Global A* has O(N!) complexity. For N > 8, computation would "
            "freeze. Reduce to 8 patients or select Partitioned mode."
        ),
        "sim_initializing":  "Initializing pipeline...",
        "sim_progress_text": "Processing batch {current} of {total}...",
        "sim_nodes_label":   "Nodes explored so far: {n}",
        "sim_completed":     "Completed.",
        "sim_queue_header":  "OPTIMAL QUEUE  —  A* OUTPUT",
        "sim_report_header": "PERFORMANCE REPORT",
        "sim_audit_header":  "QUEUE AUDIT",
        "sim_audit_info": (
            "Export the attendance order or inspect the permutation matrices per algorithm."
        ),
        "sim_download_btn": "Download A* Data (CSV)",
        "sim_audit_astar":  "Permutation Matrix: A* Search",
        "sim_audit_greedy": "Permutation Matrix: Greedy Heuristic",
        "sim_audit_fifo":   "Permutation Matrix: FIFO Approximation",

        # KPIs
        "kpi_exec_time":       "Execution Time",
        "kpi_exec_help":       "Full pipeline wall-clock: generation + inference + optimization.",
        "kpi_nodes":           "Nodes Explored (A*)",
        "kpi_nodes_help":      "Total heap expansions across all processed batches.",
        "kpi_wait_fifo":       "Avg Wait - FIFO",
        "kpi_wait_fifo_help":  "Average accumulated wait time per patient in FIFO.",
        "kpi_wait_astar":      "Avg Wait - A*",
        "kpi_wait_astar_help": "Average accumulated wait time per patient in A*.",

        # Charts
        "chart_risk_title":    "Global Accumulated Risk — Strategy Comparison",
        "chart_profile_title": "Clinical Profile — Manchester Protocol",
        "chart_x_risk":        "Numeric Risk",
        "chart_y_patients":    "Patient Volume",
        "chart_fifo":          "FIFO",
        "chart_greedy":        "Greedy",
        "chart_astar":         "A* (Optimizer)",

        # Metrics
        "metric_fifo":        "Accumulated Risk - FIFO",
        "metric_greedy":      "Accumulated Risk - Greedy",
        "metric_astar":       "Accumulated Risk - A*",
        "metric_delta_label": "vs Greedy",

        # Patient cards
        "card_prefix":    "PAC",
        "card_risk_high": "HIGH",
        "card_risk_med":  "MED",
        "card_risk_low":  "LOW",

        # Manchester display names
        "manch_nao_urgente":   "Not Urgent",
        "manch_pouco_urgente": "Standard",
        "manch_urgente":       "Urgent",
        "manch_muito_urgente": "Very Urgent",
        "manch_emergencia":    "Emergency",

        # Methodology — base
        "method_title":    "Methodology",
        "method_subtitle": "Theoretical framework, causal modeling and triage protocol.",

        # Methodology — Bayesian Network
        "method_bn_header": "Diagnostic Bayesian Network",
        "method_bn_desc": (
            "The network encapsulates clinical knowledge about the relationship between "
            "risk factors and the severity of patient condition. Each node represents a "
            "binary clinical variable; each arc represents a direct causal dependency."
        ),
        "method_graph_title": "Causal Graph",
        "method_arcs_header": "Causal Relations",
        "method_arc_from":    "Source Node",
        "method_arc_to":      "Target Node",
        "method_arc_meaning": "Clinical Interpretation",

        # Methodology — metrics
        "method_metrics_header": "Graph Structural Metrics",
        "method_metric_nodes":   "Total Nodes",
        "method_metric_arcs":    "Total Arcs",
        "method_metric_roots":   "Root Nodes",
        "method_metric_cpt":     "CPT Combinations",

        # Methodology — legends
        "method_legend_root":   "Root Nodes — no parents: AdvancedAge, Fever, PainLevel",
        "method_legend_inter":  "Intermediate Nodes — ChronicDisease, O2Saturation, HeartRate",
        "method_legend_target": "Target Node — Severity (3 states: low, medium, high)",

        # Methodology — Variable Elimination
        "method_ve_header": "Exact Inference — Variable Elimination",
        "method_ve_body": (
            "Probabilistic inference is performed by the exact *Variable Elimination* "
            "(VE) algorithm, which computes the marginal distribution of the target node "
            "`Severity` conditioned on observed evidence, iteratively eliminating latent "
            "variables via factor multiplication and marginalization. The output is a "
            "normalized probability vector `{low, medium, high}`. A **memoization** layer "
            "keyed by SHA-256 hash of the evidence set caches previously computed results, "
            "reducing repeated inferences from $O(2^n)$ to amortized $O(1)$ — critical "
            "for latency under high-load simulations."
        ),

        # Methodology — Complexity
        "method_complexity_header": "Computational Complexity & Mitigation",
        "method_complexity_body": (
            "The triage queue state space grows **factorially** with the number of "
            "patients $N$: exhaustive enumeration has complexity $\\mathcal{O}(N!)$, "
            "making queues with $N > 10$ infeasible. The module implements a "
            "**Sliding Window** strategy with size $k = 8$: the queue is partitioned "
            "into $\\lceil N/k \\rceil$ batches and A* is applied locally to each batch, "
            "reducing effective complexity to "
            "$\\mathcal{O}(\\lceil N/k \\rceil \\times k!)$. An **initial-risk "
            "partitioning heuristic** orders batches by severity probability, mitigating "
            "'batch myopia' and preserving global solution quality."
        ),

        # Methodology — Cost functions
        "method_math_header": "Cost Functions",
        "method_math_desc":   "The A* engine parameterizes two clinical deterioration functions:",
        "method_table_range": "Probability Range",
        "method_table_cat":   "Category",
        "method_table_color": "Color",

        # Methodology — Empirical
        "method_empirical_header": "Empirical Results",
        "method_empirical_body": (
            "Experiments in overcrowding scenarios ($N = 100$ patients) demonstrated "
            "that under **exponential penalty** ($\\tau = 60$ min), the Partitioned A* "
            "strategy outperforms the Greedy Heuristic by more than "
            "**50% reduction in global accumulated risk**. Under a linear function, "
            "the difference is marginal, indicating that A*'s advantage is most "
            "pronounced in high-criticality scenarios with nonlinear deterioration."
        ),

        # Methodology — Manchester
        "method_manchester_header": "Manchester Protocol — Category Mapping",
        "method_manchester_desc": (
            "Mapping of continuous high-severity probability $[0, 1]$ to five clinical "
            "categories with uniform thresholds $\\Delta = 0.20$."
        ),

        # Methodology — Conclusions
        "method_conclusions_header": "Research Conclusions & Impact",
        "method_conclusion_1_title": "Validity of the Hybrid Architecture",
        "method_conclusion_1_body": (
            "The integration of Symbolic AI (Bayesian Network for causal inference under "
            "uncertainty) with Operations Research (A* search for combinatorial "
            "optimization) proved architecturally sound. Each component is isolated by "
            "Pydantic-typed interfaces, ensuring immutability and independent testability. "
            "The separation of concerns — inference, risk function, optimization and "
            "rendering — allows replacement of any module without regression."
        ),
        "method_conclusion_2_title": "A* Superiority under Exponential Penalty",
        "method_conclusion_2_body": (
            "Experiments confirm the central hypothesis: greedy algorithms suffice for "
            "linear cost functions (O(N log N) time complexity), but fail systematically "
            "in high-criticality scenarios with exponential penalties. Partitioned A* "
            "demonstrated over 50% risk reduction in these scenarios, validating the "
            "need for heuristic state-space exploration in high-urgency clinical contexts."
        ),
        "method_conclusion_3_title": "Practical Implications & Future Work",
        "method_conclusion_3_body": (
            "The system constitutes a simulation and validation environment for scheduling "
            "algorithms under clinical uncertainty. For real hospital adoption, future work "
            "should include: (1) calibrating CPTs with real clinical data; (2) evaluating "
            "the risk function with medical experts; (3) integration with Electronic Health "
            "Record (EHR) systems; and (4) fairness evaluation to detect potential bias "
            "in synthetic data."
        ),

        # Footer
        "footer_by":        "Developed by Hugo Mendes",
        "footer_github":    "GitHub",
        "footer_linkedin":  "LinkedIn",
        "footer_portfolio": "Portfolio",
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_t(lang: str) -> Dict[str, Any]:
    """Returns the translation dictionary for the given language code.

    Args:
        lang: Language code ('pt' or 'en'). Falls back to 'pt' for unknown codes.

    Returns:
        Dictionary mapping i18n keys to localized strings.
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["pt"])


def get_node_labels(lang: str) -> Dict[str, str]:
    """Returns BN node display-name mapping for the given language.

    Args:
        lang: Language code ('pt' or 'en').

    Returns:
        Dictionary mapping internal node names to localized display names.
    """
    return NODE_LABELS.get(lang, NODE_LABELS["pt"])
