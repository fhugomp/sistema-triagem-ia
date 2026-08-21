"""
Pagina: 3_Methodology
Whitepaper tecnico: Rede Bayesiana com labels dinamicos, complexidade computacional,
funcoes de custo, Protocolo de Manchester e conclusoes da pesquisa.
"""

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.ui.components import (
    PALETA_MANCHESTER,
    _CATEGORIAS_MANCHESTER,
    _LIMIARES_MANCHESTER,
    injetar_css_global,
    renderizar_navbar,
    renderizar_rodape,
)
from src.ui.i18n import get_node_labels, get_t

st.set_page_config(
    page_title="TRIAGE.AI — Methodology",
    layout="wide",
    initial_sidebar_state="collapsed",
)

injetar_css_global()
st.markdown('<span class="methodology-page-marker"></span>', unsafe_allow_html=True)

if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"
lang = st.session_state["lang"]
t = get_t(lang)

renderizar_navbar(t, lang)

# ---------------------------------------------------------------------------
# Cabecalho
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div style="padding:8px 0 20px 0;">
        <h1 style="font-size:36px; font-weight:700; letter-spacing:-1px;
                   color:#F5F7FA; margin:0 0 6px 0; font-family:'Inter',sans-serif;">
            {t["method_title"]}
        </h1>
        <p style="color:#8b93a7; font-size:15px; font-weight:300; margin:0;
                  font-family:'Inter',sans-serif;">
            {t["method_subtitle"]}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 32px 0;">',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Rede Bayesiana — Grafo Interativo com labels dinamicos por idioma
# ---------------------------------------------------------------------------

st.subheader(t["method_bn_header"])
st.markdown(t["method_bn_desc"])

# Grafo e layout sao cacheados; labels sao re-mapeados por idioma em runtime
@st.cache_resource
def construir_grafo_e_posicoes() -> tuple[nx.DiGraph, dict[str, tuple[float, float]]]:
    """Constroi o grafo causal e define posicoes (invariantes por idioma)."""
    arestas = [
        ("IdadeAvancada",      "DoencaCronica"),
        ("IdadeAvancada",      "Gravidade"),
        ("DoencaCronica",      "SaturacaoO2"),
        ("DoencaCronica",      "Gravidade"),
        ("SaturacaoO2",        "Gravidade"),
        ("Febre",              "FrequenciaCardiaca"),
        ("FrequenciaCardiaca", "Gravidade"),
        ("NivelDor",           "Gravidade"),
        ("Febre",              "Gravidade"),
    ]
    G: nx.DiGraph = nx.DiGraph()
    G.add_edges_from(arestas)
    posicoes: dict[str, tuple[float, float]] = {
        "IdadeAvancada":      (0.0, 0.8),
        "DoencaCronica":      (1.6, 0.8),
        "SaturacaoO2":        (3.2, 0.8),
        "Febre":              (0.0, 0.2),
        "FrequenciaCardiaca": (1.6, 0.2),
        "NivelDor":           (3.2, 0.2),
        "Gravidade":          (5.0, 0.5),
    }
    return G, posicoes


G, posicoes = construir_grafo_e_posicoes()

# Translate node labels for current language
node_labels_map = get_node_labels(lang)

NOS_RAIZ = {"IdadeAvancada", "Febre", "NivelDor"}
NO_ALVO  = {"Gravidade"}
COR_RAIZ = "#3b82f6"
COR_INTER = "#10b981"
COR_ALVO  = "#ef4444"

def _cor_no(nome: str) -> str:
    if nome in NOS_RAIZ:
        return COR_RAIZ
    if nome in NO_ALVO:
        return COR_ALVO
    return COR_INTER

# Arcs
aresta_x: list[float | None] = []
aresta_y: list[float | None] = []
for orig, dest in G.edges():
    x0, y0 = posicoes[orig]
    x1, y1 = posicoes[dest]
    aresta_x += [x0, x1, None]
    aresta_y += [y0, y1, None]

trace_arestas = go.Scatter(
    x=aresta_x, y=aresta_y, mode="lines",
    line=dict(width=2, color="rgba(255,255,255,0.2)"),
    hoverinfo="none",
)

nos_list = list(G.nodes())
nos_x = [posicoes[n][0] for n in nos_list]
nos_y = [posicoes[n][1] for n in nos_list]
nos_cores = [_cor_no(n) for n in nos_list]
# Dynamic display labels per language
nos_labels = [node_labels_map.get(n, n) for n in nos_list]
nos_hover = [
    f"<b>{node_labels_map.get(n, n)}</b><br>Parents: {G.in_degree(n)}"
    f"<br>Children: {G.out_degree(n)}"
    for n in nos_list
]

trace_nos = go.Scatter(
    x=nos_x, y=nos_y, mode="markers+text",
    marker=dict(size=44, color=nos_cores, line=dict(width=2, color="#080A0F")),
    text=nos_labels, textposition="top center",
    textfont=dict(size=11, color="#F5F7FA"),
    hovertext=nos_hover, hoverinfo="text",
)

total_nos = G.number_of_nodes()
total_arcos = G.number_of_edges()
fig_grafo = go.Figure(
    data=[trace_arestas, trace_nos],
    layout=go.Layout(
        title=dict(
            text=f"{t['method_graph_title']} — {total_nos} nodes, {total_arcos} arcs",
            font=dict(size=14, color="#F5F7FA"),
        ),
        showlegend=False, hovermode="closest",
        margin=dict(t=50, b=20, l=20, r=20), height=400,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    ),
)
st.plotly_chart(fig_grafo, use_container_width=True, key="method_bn_graph")

col_leg1, col_leg2, col_leg3 = st.columns(3)
with col_leg1:
    st.markdown(
        f"<span style='color:{COR_RAIZ}; font-weight:bold;'>&#9679;</span> "
        f"{t['method_legend_root']}",
        unsafe_allow_html=True,
    )
with col_leg2:
    st.markdown(
        f"<span style='color:{COR_INTER}; font-weight:bold;'>&#9679;</span> "
        f"{t['method_legend_inter']}",
        unsafe_allow_html=True,
    )
with col_leg3:
    st.markdown(
        f"<span style='color:{COR_ALVO}; font-weight:bold;'>&#9679;</span> "
        f"{t['method_legend_target']}",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Variable Elimination — Inferencia Exata
# ---------------------------------------------------------------------------

st.subheader(t["method_ve_header"])
st.markdown(t["method_ve_body"])

st.markdown("---")

# ---------------------------------------------------------------------------
# Tabela de arcos causais
# ---------------------------------------------------------------------------

st.subheader(t["method_arcs_header"])

arcos_pt = [
    ("IdadeAvancada",       "DoencaCronica",      "Idade avancada eleva prevalencia de doencas cronicas"),
    ("IdadeAvancada",       "Gravidade",           "Idosos apresentam maior probabilidade de quadros graves"),
    ("DoencaCronica",       "SaturacaoO2",         "Comorbidades reduzem a saturacao de oxigenio"),
    ("DoencaCronica",       "Gravidade",           "Doenca cronica e fator direto de agravamento"),
    ("SaturacaoO2",         "Gravidade",           "Saturacao baixa e indicador critico de deterioracao"),
    ("Febre",               "FrequenciaCardiaca",  "Processo febril eleva a frequencia cardiaca"),
    ("FrequenciaCardiaca",  "Gravidade",           "Taquicardia e correlacionada a quadros graves"),
    ("NivelDor",            "Gravidade",           "Dor intensa e sinal de urgencia clinica"),
    ("Febre",               "Gravidade",           "Febre persistente contribui diretamente para gravidade"),
]
arcos_en = [
    ("AdvancedAge",   "ChronicDisease",  "Advanced age increases prevalence of chronic disease"),
    ("AdvancedAge",   "Severity",        "Elderly patients have higher probability of severe conditions"),
    ("ChronicDisease","O2Saturation",    "Comorbidities reduce oxygen saturation"),
    ("ChronicDisease","Severity",        "Chronic disease is a direct severity factor"),
    ("O2Saturation",  "Severity",        "Low saturation is a critical deterioration indicator"),
    ("Fever",         "HeartRate",       "Febrile process elevates heart rate"),
    ("HeartRate",     "Severity",        "Tachycardia is correlated with severe conditions"),
    ("PainLevel",     "Severity",        "Intense pain is a sign of clinical urgency"),
    ("Fever",         "Severity",        "Persistent fever contributes directly to severity"),
]

arcos = arcos_en if lang == "en" else arcos_pt
df_arcos = pd.DataFrame(
    arcos,
    columns=[t["method_arc_from"], t["method_arc_to"], t["method_arc_meaning"]],
)
st.dataframe(df_arcos, use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Metricas estruturais
# ---------------------------------------------------------------------------

st.subheader(t["method_metrics_header"])
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(t["method_metric_nodes"], G.number_of_nodes())
with col_m2:
    st.metric(t["method_metric_arcs"], G.number_of_edges())
with col_m3:
    st.metric(t["method_metric_roots"], len(NOS_RAIZ))
with col_m4:
    st.metric(t["method_metric_cpt"], f"2^6 = {2**6}")

st.markdown("---")

# ---------------------------------------------------------------------------
# Complexidade Computacional e Mitigacao
# ---------------------------------------------------------------------------

st.subheader(t["method_complexity_header"])
st.markdown(t["method_complexity_body"])

st.markdown("---")

# ---------------------------------------------------------------------------
# Funcoes de custo
# ---------------------------------------------------------------------------

st.subheader(t["method_math_header"])
st.markdown(t["method_math_desc"])

col_math1, col_math2 = st.columns(2)
with col_math1:
    st.markdown(
        """
        **Linear**

        $$f(t) = P(Alta) \\times t$$

        Risco cresce proporcionalmente ao tempo de espera.
        """
        if lang == "pt" else
        """
        **Linear**

        $$f(t) = P(High) \\times t$$

        Risk grows proportionally to waiting time.
        """
    )
with col_math2:
    st.markdown(
        r"""
        **Exponencial**

        $$f(t) = P(Alta) \times e^{t / \tau}, \quad \tau = 60 \text{ min}$$

        Risco escala rapidamente — simula deterioracao abrupta em quadros criticos.
        """
        if lang == "pt" else
        r"""
        **Exponential**

        $$f(t) = P(High) \times e^{t / \tau}, \quad \tau = 60 \text{ min}$$

        Risk scales rapidly — simulates abrupt deterioration in critical conditions.
        """
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Resultados Empiricos
# ---------------------------------------------------------------------------

st.subheader(t["method_empirical_header"])

col_hl, col_body = st.columns([1, 3], vertical_alignment="center")
with col_hl:
    st.markdown(
        f"""
        <div class="highlight-box">
            <div class="highlight-value">&gt;50%</div>
            <div class="highlight-label">{t["hl_risk_reduction"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_body:
    st.markdown(t["method_empirical_body"])

st.markdown("---")

# ---------------------------------------------------------------------------
# Protocolo de Manchester
# ---------------------------------------------------------------------------

st.subheader(t["method_manchester_header"])
st.markdown(t["method_manchester_desc"])

manch_display_keys = [
    "manch_nao_urgente", "manch_pouco_urgente", "manch_urgente",
    "manch_muito_urgente", "manch_emergencia",
]
cores_display_pt = ["Azul", "Verde", "Amarelo", "Laranja", "Vermelho"]
cores_display_en = ["Blue", "Green", "Yellow", "Orange", "Red"]
cores_display = cores_display_en if lang == "en" else cores_display_pt
cores_hex = list(PALETA_MANCHESTER.values())

manch_rows = []
for i, (cat_key, cat_interno) in enumerate(
    zip(manch_display_keys, _CATEGORIAS_MANCHESTER)
):
    faixa = f"[{_LIMIARES_MANCHESTER[i]:.2f} — {_LIMIARES_MANCHESTER[i+1]:.2f})"
    manch_rows.append(
        {
            t["method_table_range"]: faixa,
            t["method_table_cat"]: t.get(cat_key, cat_interno),
            t["method_table_color"]: f"{cores_display[i]} ({cores_hex[i]})",
        }
    )

# Corrige fechamento do ultimo intervalo
manch_rows[-1][t["method_table_range"]] = (
    f"[{_LIMIARES_MANCHESTER[-2]:.2f} — {_LIMIARES_MANCHESTER[-1]:.2f}]"
)

st.dataframe(pd.DataFrame(manch_rows), use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Conclusoes da Pesquisa & Impacto
# ---------------------------------------------------------------------------

st.subheader(t["method_conclusions_header"])

for i in range(1, 4):
    title_key = f"method_conclusion_{i}_title"
    body_key = f"method_conclusion_{i}_body"
    st.markdown(
        f"""
        <div class="conclusion-box">
            <div class="conclusion-title">{t[title_key]}</div>
            <div class="conclusion-body">{t[body_key]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

renderizar_rodape(t)
