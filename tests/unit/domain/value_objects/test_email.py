import dataclasses

import pytest

from domain.value_objects.email import EMAIL_MAX_LENGTH, Email


def test_cria_email_valido():
    """Testa a criação a partir de um endereço válido."""

    email = Email("ana.silva@oficina.com.br")

    assert email.value == "ana.silva@oficina.com.br"
    assert email.local == "ana.silva"
    assert email.dominio == "oficina.com.br"


@pytest.mark.parametrize(
    "entrada",
    ["Ana@Example.com", "  ana@example.com  ", "ANA@EXAMPLE.COM"],
)
def test_normalizacao(entrada):
    """Testa que espaços são removidos e o endereço vai para minúsculas."""

    assert Email(entrada).value == "ana@example.com"


def test_igualdade_por_valor():
    """Testa que variações de caixa são o mesmo e-mail."""

    assert Email("Ana@Example.com") == Email("ana@example.com")
    assert hash(Email("Ana@Example.com")) == hash(Email("ana@example.com"))
    assert len({Email("Ana@Example.com"), Email(" ana@example.com ")}) == 1


@pytest.mark.parametrize("entrada", [None, "", "   ", 42])
def test_email_obrigatorio(entrada):
    """Testa a rejeição de valores vazios ou de outro tipo."""

    with pytest.raises(ValueError):
        Email(entrada)


@pytest.mark.parametrize(
    "entrada",
    [
        "abc",
        "ana.example.com",
        "@example.com",
        "ana@",
        "ana@example",
        "ana@@example.com",
        "ana silva@example.com",
    ],
)
def test_formatos_invalidos(entrada):
    """Testa a rejeição de endereços malformados."""

    with pytest.raises(ValueError, match="E-mail inválido"):
        Email(entrada)


def test_tamanho_maximo():
    """Testa o limite imposto pela coluna VARCHAR(150)."""

    dominio = "@example.com"
    no_limite = "a" * (EMAIL_MAX_LENGTH - len(dominio)) + dominio
    acima = "a" * (EMAIL_MAX_LENGTH - len(dominio) + 1) + dominio

    assert len(Email(no_limite).value) == EMAIL_MAX_LENGTH

    with pytest.raises(ValueError, match="no máximo 150 caracteres"):
        Email(acima)


def test_e_imutavel():
    """Testa que o endereço não pode ser alterado após a criação."""

    email = Email("ana@example.com")

    with pytest.raises(dataclasses.FrozenInstanceError):
        email.value = "outro@example.com"


def test_str_devolve_o_endereco():
    """Testa a conversão para texto, usada na persistência."""

    assert str(Email("Ana@Example.com")) == "ana@example.com"
