import pytest
from pydantic import ValidationError
from src.models.paciente import Paciente


def test_construcao_paciente_valido() -> None:
    """Verifica se o paciente é construído corretamente e se os aliases funcionam."""
    p = Paciente(
        id_paciente=1,
        idade_anos=65,
        idade_avancada="Verdadeiro",
        doenca_cronica="Falso",
        saturacao_o2="Normal",
        frequencia_cardiaca="Normal",
        nivel_dor="Leve",
        febre="Ausente",
        tempo_espera_inicial_minutos=30
    )
    assert p.id_paciente == 1
    assert p.idade_anos == 65
    assert p.idade_avancada == "Verdadeiro"
    assert p.probabilidade_alta == 0.0


def test_rejeicao_idade_acima_limite() -> None:
    """Verifica se o modelo rejeita idades inválidas (> 120)."""
    with pytest.raises(ValidationError) as exc_info:
        Paciente(
            id_paciente=1,
            idade_anos=150,
            idade_avancada="Verdadeiro",
            doenca_cronica="Falso",
            saturacao_o2="Normal",
            frequencia_cardiaca="Normal",
            nivel_dor="Leve",
            febre="Ausente",
            tempo_espera_inicial_minutos=30
        )
    assert "Input should be less than or equal to 120" in str(exc_info.value)


def test_rejeicao_probabilidade_fora_intervalo() -> None:
    """Verifica se a probabilidade está limitada a [0, 1]."""
    with pytest.raises(ValidationError) as exc_info:
        Paciente(
            id_paciente=1,
            idade_anos=65,
            idade_avancada="Verdadeiro",
            doenca_cronica="Falso",
            saturacao_o2="Normal",
            frequencia_cardiaca="Normal",
            nivel_dor="Leve",
            febre="Ausente",
            tempo_espera_inicial_minutos=30,
            probabilidade_alta=1.5
        )
    assert "Input should be less than or equal to 1" in str(exc_info.value)


def test_rejeicao_literal_invalido() -> None:
    """Verifica se o tipo Literal previne valores arbitrários."""
    with pytest.raises(ValidationError) as exc_info:
        Paciente(
            id_paciente=1,
            idade_anos=65,
            idade_avancada="Verdadeiro",
            doenca_cronica="Falso",
            saturacao_o2="Normal",
            frequencia_cardiaca="Normal",
            nivel_dor="Leve",
            febre="Sim",  # Inválido
            tempo_espera_inicial_minutos=30
        )
    assert "Input should be" in str(exc_info.value)


def test_imutabilidade_frozen() -> None:
    """Verifica se o objeto é imutável (frozen)."""
    p = Paciente(
        id_paciente=1,
        idade_anos=65,
        idade_avancada="Verdadeiro",
        doenca_cronica="Falso",
        saturacao_o2="Normal",
        frequencia_cardiaca="Normal",
        nivel_dor="Leve",
        febre="Ausente",
        tempo_espera_inicial_minutos=30
    )
    with pytest.raises(ValidationError) as exc_info:
        p.idade_anos = 70
    assert "Instance is frozen" in str(exc_info.value)


def test_propriedade_evidencias_bayesianas() -> None:
    """Verifica a extração das evidências para a Rede Bayesiana."""
    p = Paciente(
        id_paciente=1,
        idade_anos=65,
        idade_avancada="Verdadeiro",
        doenca_cronica="Falso",
        saturacao_o2="Normal",
        frequencia_cardiaca="Normal",
        nivel_dor="Leve",
        febre="Ausente",
        tempo_espera_inicial_minutos=30
    )
    evidencias = p.evidencias_bayesianas
    assert evidencias == {
        "IdadeAvancada": "Verdadeiro",
        "DoencaCronica": "Falso",
        "SaturacaoO2": "Normal",
        "FrequenciaCardiaca": "Normal",
        "NivelDor": "Leve",
        "Febre": "Ausente",
    }
