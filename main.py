"""
Entrypoint principal — TRIAGE.AI Overview.
Apresenta o sistema, sua arquitetura e direciona para os modulos.
"""

import streamlit as st

from src.ui.components import injetar_css_global, renderizar_navbar, renderizar_rodape
from src.ui.i18n import get_t

st.set_page_config(
    page_title="TRIAGE.AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

injetar_css_global()

if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"
lang = st.session_state["lang"]
t = get_t(lang)

renderizar_navbar(t, lang)

# ---------------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------------

# Build hero title — replace \n with <br> for HTML rendering
_hero_lines = t["hero_title"].replace("\n", "<br>")

st.markdown(
    f"""
    <div style="text-align:center; padding: 48px 0 40px 0;">
        <div style="font-size:11px; font-weight:700; letter-spacing:3px;
                    color:#8b5cf6; text-transform:uppercase; margin-bottom:18px;
                    font-family:'Inter',sans-serif;">
            &#9672; TRIAGE.AI
        </div>
        <h1 style="font-size:50px; font-weight:700; letter-spacing:-1.5px;
                   color:#F5F7FA; margin:0 0 18px 0; line-height:1.08;
                   font-family:'Inter',sans-serif;">
            {_hero_lines}
        </h1>
        <p style="font-size:18px; color:#8b93a7; font-weight:300;
                  max-width:540px; margin:0 auto; font-family:'Inter',sans-serif;">
            {t["overview_hero_sub"]}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# CTA button — uses st.page_link for native Streamlit navigation
_, col_cta, _ = st.columns([3, 2, 3])
with col_cta:
    st.markdown('<div class="hero-btn">', unsafe_allow_html=True)
    st.page_link(
        "pages/2_Simulation.py",
        label=t["hero_cta"],
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:20px 0 40px 0;">',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Architecture cards
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="section-label">{t["overview_arch_header"]}</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="medium")
_cards = [
    ("mod_01_num", "mod_01_title", "mod_01_desc"),
    ("mod_02_num", "mod_02_title", "mod_02_desc"),
    ("mod_03_num", "mod_03_title", "mod_03_desc"),
]

for col, (k_num, k_title, k_desc) in zip([col1, col2, col3], _cards):
    with col:
        st.markdown(
            f"""
            <div class="module-card">
                <div class="module-number">{t[k_num]}</div>
                <div class="module-title">{t[k_title]}</div>
                <div class="module-desc">{t[k_desc]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    '<div style="height:40px;"></div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Technical stats pills
# ---------------------------------------------------------------------------

sc1, sc2, sc3, sc4 = st.columns(4, gap="medium")
_stats = [
    ("7",  "hl_nodes"),
    ("9",  "hl_arcs"),
    ("64", "hl_cpt"),
    ("5",  "hl_manch"),
]

for col, (value, key) in zip([sc1, sc2, sc3, sc4], _stats):
    with col:
        st.markdown(
            f"""
            <div class="stat-pill">
                <div class="stat-value">{value}</div>
                <div class="stat-label">{t[key]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:36px;"></div>', unsafe_allow_html=True)

renderizar_rodape(t)

