"""
Testes do mapeamento Protocolo de Manchester e da paleta de cores oficial.
Cobre: classificar_manchester(), PALETA_MANCHESTER e limites de categoria.
"""

import pytest

from src.ui.components import classificar_manchester, PALETA_MANCHESTER, _CATEGORIAS_MANCHESTER


# ---------------------------------------------------------------------------
# Classificacao por categoria
# ---------------------------------------------------------------------------


def test_classificar_manchester_nao_urgente() -> None:
    """Probabilidade em [0.00, 0.20) deve resultar em 'Nao Urgente' (Azul)."""
    assert classificar_manchester(0.00) == "Nao Urgente"
    assert classificar_manchester(0.10) == "Nao Urgente"
    assert classificar_manchester(0.19) == "Nao Urgente"


def test_classificar_manchester_pouco_urgente() -> None:
    """Probabilidade em [0.20, 0.40) deve resultar em 'Pouco Urgente' (Verde)."""
    assert classificar_manchester(0.20) == "Pouco Urgente"
    assert classificar_manchester(0.30) == "Pouco Urgente"
    assert classificar_manchester(0.39) == "Pouco Urgente"


def test_classificar_manchester_urgente() -> None:
    """Probabilidade em [0.40, 0.60) deve resultar em 'Urgente' (Amarelo)."""
    assert classificar_manchester(0.40) == "Urgente"
    assert classificar_manchester(0.50) == "Urgente"
    assert classificar_manchester(0.59) == "Urgente"


def test_classificar_manchester_muito_urgente() -> None:
    """Probabilidade em [0.60, 0.80) deve resultar em 'Muito Urgente' (Laranja)."""
    assert classificar_manchester(0.60) == "Muito Urgente"
    assert classificar_manchester(0.70) == "Muito Urgente"
    assert classificar_manchester(0.79) == "Muito Urgente"


def test_classificar_manchester_emergencia() -> None:
    """Probabilidade em [0.80, 1.00] deve resultar em 'Emergencia' (Vermelho)."""
    assert classificar_manchester(0.80) == "Emergencia"
    assert classificar_manchester(0.90) == "Emergencia"
    assert classificar_manchester(1.00) == "Emergencia"


# ---------------------------------------------------------------------------
# Limites e casos extremos
# ---------------------------------------------------------------------------


def test_classificar_manchester_limite_zero() -> None:
    """Probabilidade exatamente 0.0 deve ser 'Nao Urgente'."""
    assert classificar_manchester(0.0) == "Nao Urgente"


def test_classificar_manchester_limite_um() -> None:
    """Probabilidade exatamente 1.0 deve ser 'Emergencia'."""
    assert classificar_manchester(1.0) == "Emergencia"


def test_classificar_manchester_clamp_abaixo_de_zero() -> None:
    """Probabilidades abaixo de 0.0 devem ser tratadas como 0.0 (Nao Urgente)."""
    assert classificar_manchester(-0.5) == "Nao Urgente"


def test_classificar_manchester_clamp_acima_de_um() -> None:
    """Probabilidades acima de 1.0 devem ser tratadas como 1.0 (Emergencia)."""
    assert classificar_manchester(1.5) == "Emergencia"


# ---------------------------------------------------------------------------
# Integridade da paleta
# ---------------------------------------------------------------------------


def test_paleta_manchester_cinco_categorias() -> None:
    """A paleta oficial deve conter exatamente 5 categorias."""
    assert len(PALETA_MANCHESTER) == 5, (
        f"Esperado 5 categorias, obtido {len(PALETA_MANCHESTER)}."
    )


def test_paleta_manchester_cores_hexadecimais() -> None:
    """Todas as cores da paleta devem ser strings hexadecimais validas (#RRGGBB)."""
    import re
    padrao_hex = re.compile(r"^#[0-9A-Fa-f]{6}$")
    for categoria, cor in PALETA_MANCHESTER.items():
        assert padrao_hex.match(cor), (
            f"Cor invalida para '{categoria}': '{cor}'. Esperado formato #RRGGBB."
        )


def test_paleta_manchester_cobertura_categorias() -> None:
    """Todas as categorias de _CATEGORIAS_MANCHESTER devem estar na paleta."""
    for categoria in _CATEGORIAS_MANCHESTER:
        assert categoria in PALETA_MANCHESTER, (
            f"Categoria '{categoria}' ausente na PALETA_MANCHESTER."
        )


def test_classificar_manchester_retorna_categoria_valida() -> None:
    """Para qualquer probabilidade em [0, 1], a categoria retornada deve existir na paleta."""
    probabilidades = [i / 100 for i in range(0, 101)]
    for prob in probabilidades:
        categoria = classificar_manchester(prob)
        assert categoria in PALETA_MANCHESTER, (
            f"Categoria '{categoria}' para prob={prob} nao encontrada na paleta."
        )
