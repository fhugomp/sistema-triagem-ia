<div align="center">

# TRIAGE.AI

### Intelligent Clinical Queue Optimization

[![Streamlit App](https://img.shields.io/badge/Streamlit-Demo-red?logo=streamlit)](https://sistemadetriagem.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-green)](https://docs.pydantic.dev/)
[![Versao](https://img.shields.io/badge/Versao-2.0-8B5CF6)](https://github.com/fhugomp/sistema-triagem-ia)

</div>

<p align="center">
  <img src="docs/sistemadetriagem_capa.png" alt="TRIAGE.AI" width="900">
</p>

<div align="center">

Plataforma experimental de simulação de triagem médica baseada em Inteligência Artificial.

A versão 2.0 entrega uma interface **Dark Mode** com suporte a internacionalização
(PT-BR / EN), visualização em streaming frame-a-frame e arquitetura de backend rigorosamente tipada com Pydantic.

</div>

## Demonstracao Online

> **Nota:** Caso a aplicacao esteja em modo de espera, clique em "Yes, get this app back up!" para reativa-la.

> https://sistemadetriagem.streamlit.app/

---

## 1. Interface Multi-page (v2.0)

A aplicacao e estruturada em tres paginas independentes com navegacao pela sidebar do Streamlit:

| Pagina      | Arquivo                  | Conteudo                                                               |
| ----------- | ------------------------ | ---------------------------------------------------------------------- |
| Overview    | `main.py`                | Hero section, cards de arquitetura, metricas tecnicas                  |
| Simulation  | `pages/2_Simulation.py`  | Experiment Setup centralizado, streaming A\*, patient cards            |
| Methodology | `pages/3_Methodology.py` | Grafo causal interativo, formulas matematicas, Protocolo de Manchester |

### Dark Mode

O tema e definido em `.streamlit/config.toml` com a paleta SaaS/Cientifica:

```toml
[theme]
primaryColor            = "#8B5CF6"   # Violeta — acento principal
backgroundColor         = "#080A0F"   # Azul-marinho profundo
secondaryBackgroundColor = "#10131A"  # Superficie de cards
textColor               = "#F5F7FA"   # Branco suave
```

A tipografia **Inter** (Google Fonts) e injetada via CSS global em todos os componentes.

### Internacionalizacao (i18n)

Todos os textos da interface estao centralizados em `src/ui/i18n.py` no dicionario
`TRANSLATIONS`. Um toggle discreto **PT / EN** na barra de navegacao superior usa
`st.session_state` para persistir a selecao de idioma entre navegacoes de pagina.

```python
# Uso em qualquer pagina
if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"
lang = st.session_state["lang"]
t    = get_t(lang)                   # dicionario de strings localizado
```

---

## 2. Arquitetura do Backend

### 2.1. Tipagem Estrita com Pydantic

Toda a camada de dados e fundamentada em modelos Pydantic `frozen=True` garantindo
imutabilidade ao longo de todo o pipeline:

```python
class Paciente(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)
    id_paciente:       int   = Field(alias="ID_Paciente", ge=1)
    probabilidade_alta: float = Field(alias="Probabilidade_Alta",
                                       default=0.0, ge=0.0, le=1.0)
```

O dataclass `ResultadoSimulacao` encapsula todos os resultados, incluindo os KPIs de BI:

```python
@dataclass
class ResultadoSimulacao:
    lista_pacientes: List[Paciente]
    ordem_a_star:    List[int]
    risco_a_star:    float
    # KPIs v2.0
    tempo_execucao_segundos:          float
    nos_explorados_a_star:            int
    tempo_medio_espera_por_estrategia: Dict[str, float]
```

### 2.2. Rede Bayesiana Diagnostica

Grafo causal com 7 nos e 9 arcos, inferencia exata por Variable Elimination:

```
IdadeAvancada  ──────────────────────────────────────────┐
     |                                                   |
     v                                                   v
DoencaCronica ──────────────────────────────────────> Gravidade
     |                                                   ^
     v                                                   |
SaturacaoO2 ───────────────────────────────────────────┘ |
                                                         |
Febre ──────> FrequenciaCardiaca ────────────────────────┤
  └──────────────────────────────────────────────────────┤
                                                         |
NivelDor ────────────────────────────────────────────────┘
```

O no `Gravidade` possui 6 pais binarios, gerando CPT com 2^6 = 64 combinacoes.
Cache por hash de evidencias reduz consultas repetidas para O(1).

### 2.3. Protocolo de Manchester

Mapeamento de probabilidade continua de saida da RBN para 5 categorias clinicas:

| Faixa         | Categoria     | Cor                  |
| ------------- | ------------- | -------------------- |
| [0,00 — 0,20) | Nao Urgente   | Azul (`#3b82f6`)     |
| [0,20 — 0,40) | Pouco Urgente | Verde (`#10b981`)    |
| [0,40 — 0,60) | Urgente       | Amarelo (`#f59e0b`)  |
| [0,60 — 0,80) | Muito Urgente | Laranja (`#f97316`)  |
| [0,80 — 1,00] | Emergencia    | Vermelho (`#ef4444`) |

### 2.4. Algoritmo A\* e Streaming

O motor otimizador oferece dois modos de execucao:

- **A\* Global**: Espaco completo de estados. Limitado a N <= 8 (complexidade O(N!)).
- **A\* Particionado (Sliding Window)**: Complexidade reduzida para O(ceil(N/k) \* k!),
  com k = 8.

O metodo `otimizar_fila_streaming()` e um **generator Python** que faz `yield` de um
snapshot da fila otimizada apos cada lote processado. A pagina Simulation consome esse
generator para atualizar os cards e graficos frame a frame com `st.empty()`.

---

## 3. KPIs de Business Intelligence (v2.0)

| KPI                  | Descricao                                            |
| -------------------- | ---------------------------------------------------- |
| Tempo de Execucao    | Wall-clock do pipeline completo (ms)                 |
| Nos Explorados (A\*) | Soma das expansoes do heap em todos os lotes         |
| Espera Media — FIFO  | Tempo medio de espera acumulado por paciente no FIFO |
| Espera Media — A\*   | Tempo medio de espera acumulado por paciente no A\*  |

---

## 4. Requisitos e Instalacao

**Requisitos:** Python 3.10+, Poetry, Make.

```bash
# 1. Clonar
git clone https://github.com/fhugomp/sistema-triagem-ia.git && cd sistema-triagem-ia

# 2. Instalar
poetry install

# 3. Executar
make run
```

---

## 5. Validacao e Qualidade

```bash
make test       # suíte de testes (pytest)
make check-all  # lint + tipos + testes
```

### Cobertura de Testes

| Modulo                 | Cobertura                         |
| ---------------------- | --------------------------------- |
| `test_a_star.py`       | Heuristica, heapq, nos explorados |
| `test_bayesian_net.py` | Inferencia, cache, estados        |
| `test_generator.py`    | Geracao de dados sinteticos       |
| `test_paciente.py`     | Validacao Pydantic, imutabilidade |
| `test_simulator.py`    | Pipeline completo, comparativo    |
| `test_runner_kpis.py`  | KPIs de BI (tempo, nos, espera)   |
| `test_manchester.py`   | Mapeamento de cores e categorias  |
| `test_utils.py`        | Formatacao de DataFrames          |

---

## 6. Estrutura do Repositorio

```text
sistema-triagem-ia/
├── .streamlit/
│   └── config.toml             # Tema Dark Premium
├── pages/
│   ├── 2_Simulation.py         # Dashboard com streaming
│   └── 3_Methodology.py        # Whitepaper tecnico
├── src/
│   ├── config.py
│   ├── utils.py
│   ├── data/generator.py
│   ├── models/
│   │   ├── paciente.py         # Pydantic frozen model
│   │   └── bayesian_net.py     # Rede Bayesiana (pgmpy)
│   ├── optimization/
│   │   ├── a_star.py           # A* + streaming generator
│   │   ├── baselines.py
│   │   └── risk.py
│   ├── simulation/runner.py    # Pipeline + KPIs + streaming
│   └── ui/
│       ├── components.py       # Renderizacao + Manchester + cards
│       └── i18n.py             # Dicionario PT-BR / EN
├── tests/                      # 43 testes — 100% passing
├── main.py                     # Overview / Landing
├── pyproject.toml
└── Makefile
```

---

_Desenvolvido por Hugo Mendes — [GitHub](https://github.com/fhugomp) |
[LinkedIn](https://linkedin.com/in/fhugomp) |
[Portfolio](https://fhugomp.github.io)_
