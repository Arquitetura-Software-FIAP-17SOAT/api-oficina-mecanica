import pytest

from domain.entities.cliente import Cliente


def criar_cliente(**kwargs) -> Cliente:
    padrao = {
        "nome": "Maria Souza",
        "usuario_id": 1,
        "cpf_cnpj": "529.982.247-25",
        "email": "Maria@Example.com",
    }
    padrao.update(kwargs)

    return Cliente(**padrao)


def test_cria_cliente_valido():
    """Testa a criação de um cliente com dados válidos."""

    cliente = criar_cliente()

    assert cliente.id is None
    assert cliente.nome == "Maria Souza"
    assert cliente.usuario_id == 1


def test_email_e_normalizado_para_minusculas():
    """Testa a normalização do e-mail."""

    cliente = criar_cliente()

    assert str(cliente.email) == "maria@example.com"


def test_email_opcional():
    """Testa que o cliente pode ser cadastrado sem e-mail."""

    cliente = criar_cliente(email=None)

    assert cliente.email is None


def test_email_invalido():
    """Testa a rejeição de e-mail sem arroba."""

    with pytest.raises(ValueError, match="E-mail inválido"):
        criar_cliente(email="maria.example.com")


@pytest.mark.parametrize("nome", ["", "   ", None])
def test_nome_obrigatorio(nome):
    """Testa que o cliente não pode ser criado sem nome."""

    with pytest.raises(ValueError, match="deve ser preenchido"):
        criar_cliente(nome=nome)


def test_nome_com_tamanho_excedido():
    """Testa o limite de 150 caracteres do nome."""

    with pytest.raises(ValueError, match="no máximo 150 caracteres"):
        criar_cliente(nome="a" * 151)


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("529.982.247-25", "52998224725"),
        ("52998224725", "52998224725"),
        ("11.222.333/0001-81", "11222333000181"),
    ],
)
def test_cpf_cnpj_e_normalizado_para_digitos(entrada, esperado):
    """Testa que a máscara é removida antes de persistir."""

    cliente = criar_cliente(cpf_cnpj=entrada)

    assert str(cliente.cpf_cnpj) == esperado


def test_cpf_cnpj_opcional():
    """Testa que o cliente pode ser cadastrado sem documento."""

    cliente = criar_cliente(cpf_cnpj=None)

    assert cliente.cpf_cnpj is None


@pytest.mark.parametrize("documento", ["123", "1234567890", "123456789012345"])
def test_cpf_cnpj_com_quantidade_invalida_de_digitos(documento):
    """Testa a rejeição de documentos fora de 11 ou 14 dígitos."""

    with pytest.raises(ValueError, match="11 dígitos"):
        criar_cliente(cpf_cnpj=documento)


@pytest.mark.parametrize("documento", ["111.111.111-11", "00000000000000"])
def test_cpf_cnpj_com_digitos_repetidos(documento):
    """Testa a rejeição de sequências repetidas."""

    with pytest.raises(ValueError, match="inválido"):
        criar_cliente(cpf_cnpj=documento)


@pytest.mark.parametrize("usuario_id", [0, -1, None])
def test_usuario_responsavel_obrigatorio(usuario_id):
    """Testa que o cliente exige um usuário responsável válido."""

    with pytest.raises(ValueError):
        criar_cliente(usuario_id=usuario_id)
