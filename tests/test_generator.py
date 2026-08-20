import pytest
from src.data.generator import GeradorPacientesSinteticos
from src.models.paciente import Paciente


@pytest.fixture
def gerador() -> GeradorPacientesSinteticos:
    """Instancia o gerador com uma seed fixa para testes determinísticos."""
    return GeradorPacientesSinteticos(seed=13)


def test_tamanho_e_colunas_dataframe(gerador: GeradorPacientesSinteticos) -> None:
    """Garante que a base sintética atende aos requisitos de tamanho e estrutura."""
    num_pacientes = 50
    pacientes = gerador.gerar_pacientes(num_pacientes)

    assert isinstance(pacientes, list)
    assert len(pacientes) == num_pacientes
    assert isinstance(pacientes[0], Paciente)
    
    p = pacientes[0]
    assert hasattr(p, "id_paciente")
    assert hasattr(p, "idade_anos")
    assert hasattr(p, "idade_avancada")
    assert hasattr(p, "doenca_cronica")
    assert hasattr(p, "saturacao_o2")
    assert hasattr(p, "frequencia_cardiaca")
    assert hasattr(p, "nivel_dor")
    assert hasattr(p, "febre")
    assert hasattr(p, "tempo_espera_inicial_minutos")


def test_compatibilidade_com_rede_bayesiana(
    gerador: GeradorPacientesSinteticos,
) -> None:
    """
    Garante que os pacientes gerados podem ser instanciados sem ValidationError
    (Pydantic Literal validation já cobre a compatibilidade).
    """
    # A simples execução sem exceção já é o teste de compatibilidade
    # pois o Pydantic validará os Literals de cada Paciente gerado.
    pacientes = gerador.gerar_pacientes(10)
    assert len(pacientes) == 10
