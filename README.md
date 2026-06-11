# Sistema Inteligente de Triagem Hospitalar

[![Streamlit App](https://img.shields.io/badge/Streamlit-Demo-red?logo=streamlit)](https://sistemadetriagem.streamlit.app/)

Este repositório documenta a implementação de um simulador de triagem médica baseado em Inteligência Artificial. O sistema propõe uma arquitetura computacional híbrida, integrando raciocínio probabilístico sob incerteza e otimização heurística, com o objetivo de mitigar o impacto da superlotação em prontos-socorros.

## Demonstração Online

A aplicação encontra-se disponível para execução diretamente no navegador através do Streamlit Cloud:

> https://sistemadetriagem.streamlit.app/

## 1. Arquitetura do Sistema

A solução é composta por dois módulos principais, orquestrados por intermédio de uma interface gráfica desenvolvida no framework `Streamlit`:

### 1.1. Inferência Bayesiana Diagnóstica (Modelagem Preditiva)
Implementada sob a biblioteca `pgmpy`, a rede bayesiana estima a probabilidade de um paciente apresentar quadro clínico de gravidade Alta, dadas as evidências sintomatológicas observadas (Idade Avançada, Doença Crônica, Saturação de O2, Frequência Cardíaca, Nível de Dor e Febre). O nó Gravidade é condicionado por seis evidências binárias, resultando em uma Tabela de Probabilidade Condicional (CPT) com 64 combinações possíveis de estados, construída programaticamente a partir de um modelo heurístico de risco clínico sintético. A inferência é processada através do algoritmo exato Variable Elimination, otimizado por uma camada de memoization que reduz consultas repetidas para um tempo de acesso médio $\mathcal{O}(1)$.

### 1.2. Motor de Busca Heurística (Inspirado em A*)
Responsável por formular a ordenação de atendimento como um problema de minimização de risco clínico global. Para contornar a explosão combinatória $\mathcal{O}(N!)$ intrínseca a filas de espera extensas, o sistema aplica o método de particionamento do espaço de estados (Sliding Window). O particionamento reduz drasticamente o custo computacional, porém sacrifica a garantia de obtenção do ótimo global. Esta abordagem limita a complexidade computacional pelo processamento independente de lotes de tamanho $k$, resultando em uma complexidade aproximada de $\mathcal{O}(\lceil N/k \rceil \times k!)$.

### 1.3. Configurações Experimentais
O simulador atua como um laboratório interativo, permitindo a comparação dinâmica dos efeitos estruturais da fila sobre a qualidade da solução. Através da interface, é possível parametrizar:

**Modelos de Deterioração Clínica (Funções de Risco):**
* Risco Linear: $f(t) = P(Alta) \times t$
* Risco Exponencial: $f(t) = P(Alta) \times e^{t/\tau}$

**Estratégias de Particionamento (Mitigação de Miopia):**
* Aproximação FIFO: Ordenação estritamente temporal.
* Risco Inicial: Ordenação heurística baseada no risco inicial do paciente, calculado pela combinação entre probabilidade de gravidade e tempo de espera inicial.

## 2. Requisitos de Ambiente

A execução do sistema requer o seguinte ambiente de desenvolvimento configurado:
* Python 3.12 ou superior
* Poetry (Gerenciamento de dependências e ambientes virtuais)
* Make (Automação de rotinas de validação)

## 3. Instruções de Instalação e Execução

1. Realize a clonagem do repositório localmente:
```bash
git clone https://github.com/fhugomp/sistema-triagem-ia.git
```

2. Abra a pasta do projeto:
```bash
cd sistema-triagem-ia
```

3. Instale as dependências via Poetry:
```bash
poetry install
```

4. Inicialize a interface de simulação:
```bash
make run
```

## 4. Validação e Qualidade de Software

A base de código é submetida a uma esteira rigorosa de validação, englobando testes lógicos unitários (Pytest), análise estática de tipagem (Mypy) e formatação padronizada (Ruff).

Para executar a suíte de testes lógicos de forma isolada:

```bash
make test
```

Para executar a esteira de validação e verificação completa:

```bash
make check-all
```

## 5. Estrutura do Repositório

```text
sistema-triagem-ia/
├── src/
│   ├── data/
│   ├── models/
│   ├── optimization/
│   ├── config.py
│   └── main.py
├── tests/
├── pyproject.toml
├── Makefile
└── README.md
```

### Principais Componentes
```text
bayesian_net.py   -   Inferência probabilística
a_star.py   -   Busca heurística
baselines.py   -   Estratégias FIFO e Gulosa
generator.py   -   Geração de pacientes sintéticos
main.py   -   Interface Streamlit
```

## 6. Considerações Metodológicas

O presente simulador constitui um ambiente experimental focado na análise do trade-off estrutural entre a otimalidade global e a viabilidade computacional. O particionamento em lotes introduz, de forma deliberada, a limitação analítica referenciada como "miopia local". Os resultados subótimos do algoritmo em cenários superlotados, quando comparados a heurísticas gulosas puras, configuram-se como o comportamento matemático esperado desta formulação, devidamente fundamentado e documentado no Relatório Técnico do projeto.
