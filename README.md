# Sistema Inteligente de Triagem Hospitalar

[![Streamlit App](https://img.shields.io/badge/Streamlit-Demo-red?logo=streamlit)](https://sistemadetriagem.streamlit.app/)

Este repositório documenta a implementação de um simulador de triagem médica baseado em Inteligência Artificial. O sistema propõe uma arquitetura computacional híbrida, integrando raciocínio probabilístico sob incerteza e otimização heurística, com o objetivo de mitigar o impacto da superlotação em prontos-socorros.

## Demonstração Online

A aplicação encontra-se disponível para execução diretamente no navegador através do Streamlit Cloud:

> https://sistemadetriagem.streamlit.app/

![Dashboard de Triagem](docs/sistemadetriagem_capa.png)

## 1. Arquitetura do Sistema

A solução é composta por módulos de *Backend* matemático orquestrados por uma interface gráfica analítica (Dashboard) desenvolvida no framework `Streamlit`:

### 1.1. Inferência Bayesiana Diagnóstica (Modelagem Preditiva)
Implementada sob a biblioteca `pgmpy`, a rede bayesiana estima a probabilidade de um paciente apresentar quadro clínico de gravidade Alta, dadas as evidências sintomatológicas observadas (Idade Avançada, Doença Crônica, Saturação de O2, Frequência Cardíaca, Nível de Dor e Febre). O nó Gravidade é condicionado por seis evidências binárias, resultando em uma Tabela de Probabilidade Condicional (CPT) com 64 combinações possíveis de estados. A inferência é processada através do algoritmo exato *Variable Elimination*, otimizado por uma camada de *memoization* que reduz consultas repetidas para um tempo de acesso médio $\mathcal{O}(1)$.

### 1.2. Motor de Busca Heurística (Algoritmo A*)
Responsável por formular a ordenação de atendimento como um problema de minimização de risco clínico global. Para demonstrar o domínio sobre o *trade-off* de escalabilidade computacional, o motor oferece duas modalidades de execução:

* **A* Global (Busca Completa):** Explora o espaço de estados completo. Para evitar o travamento do sistema devido à complexidade fatorial $\mathcal{O}(N!)$, possui uma trava estrutural de segurança limitando a execução a amostras pequenas ($N \le 8$). Nesta modalidade, lidando com um espaço de permutação de até $40.320$ estados, o algoritmo permite validar empiricamente a busca por soluções ótimas.
* **A* Particionado (*Sliding Window*):** Para contornar a explosão combinatória em filas extensas ($N > 8$), o sistema aplica o método de particionamento do espaço de estados. A complexidade é mitigada para aproximadamente $\mathcal{O}(\lceil N/k \rceil \times k!)$ através do processamento independente de lotes de tamanho $k=8$. Para mitigar a "miopia de lote" introduzida por essa divisão, o algoritmo utiliza nativamente o agrupamento baseado no **Risco Inicial**.

### 1.3. Configurações Experimentais
O simulador atua como um laboratório de provas interativo, permitindo parametrizar o modelo de deterioração clínica que guia a função de custo do algoritmo:

* **Risco Linear:** $f(t) = P(Alta) \times t$
* **Risco Exponencial:** $f(t) = P(Alta) \times e^{t/\tau}$ (onde $\tau = 60$ minutos, modelando a escalada temporal de deterioração crítica).

### 1.4. Painel Analítico e Auditoria
A camada de apresentação conta com a biblioteca `plotly` para visualização de dados em padrão acadêmico e industrial:
* **Perfil Clínico (Input):** Histograma de distribuição diagnóstica mapeando o volume de pacientes gerados pela Rede Bayesiana por categoria de risco.
* **Comparativo de Risco (Output):** Contraste visual explícito entre a inércia estrutural (FIFO), o limite puramente local (Heurística Gulosa) e o motor de otimização A*.
* **Auditoria:** Exportação nativa das matrizes de permutação (.csv) e tabelas de *logs* transacionais para validação em *softwares* estatísticos de terceiros.

## 2. Requisitos de Ambiente

A execução do sistema requer o seguinte ambiente de desenvolvimento configurado:
* Python 3.12 ou superior
* Poetry (Gerenciamento de dependências e ambientes virtuais)
* Make (Automação de rotinas de validação)

## 3. Instruções de Instalação e Execução

1. Realize a clonagem do repositório localmente:
```bash
git clone [https://github.com/fhugomp/sistema-triagem-ia.git](https://github.com/fhugomp/sistema-triagem-ia.git)
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
├── docs/
├── src/
│   ├── data/
│   ├── models/
│   ├── optimization/
│   ├── config.py
├── tests/
├── pyproject.toml
├── Makefile
└── README.md
└── main.py
```

### Principais Componentes
```text
bayesian_net.py  -  Inferência probabilística
a_star.py  -  Busca heurística
baselines.py  -  Estratégias FIFO e Gulosa
generator.py  -  Geração de pacientes sintéticos
main.py  -  Interface Streamlit
```

## 6. Considerações Metodológicas e Conclusões

O presente simulador constitui um ambiente experimental robusto para a validação algorítmica de escalonamento sob incerteza. 

Experimentos conduzidos na plataforma demonstraram que, sob uma métrica de progressão linear de risco, algoritmos de tempo polinomial $\mathcal{O}(N)$ (Heurística Gulosa) são suficientes para aproximar soluções satisfatórias. Contudo, em cenários representativos de superlotação ($N=100$) avaliados sob **penalidade exponencial** — refletindo o rápido agravamento de quadros clínicos críticos —, estratégias gulosas puramente locais sofrem degradação acentuada. Neste contexto, o **A* Particionado demonstrou superioridade algorítmica**, reduzindo o risco acumulado global em mais de 50%, evidenciando sua eficácia no balanceamento entre criticidade absoluta inicial e latência progressiva de fila.

Nota: Os resultados baseiam-se em dados gerados estocasticamente. Trabalhos futuros devem englobar validações clínicas com bases de pacientes reais para a calibração de hiperparâmetros (como o fator $\tau$) e a inferência das Tabelas de Probabilidade Condicional.
