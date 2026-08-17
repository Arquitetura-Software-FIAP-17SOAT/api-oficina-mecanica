import dataclasses

import pytest

from domain.value_objects.cpf_cnpj import CpfCnpj

CPF_VALIDO = "529.982.247-25"
CNPJ_VALIDO = "11.222.333/0001-81"


def test_cria_cpf_valido():
    """Testa a criação a partir de um CPF com máscara."""

    documento = CpfCnpj(CPF_VALIDO)

    assert documento.value == "52998224725"
    assert documento.is_cpf is True
    assert documento.tipo == "CPF"


def test_cria_cnpj_valido():
    """Testa a criação a partir de um CNPJ com máscara."""

    documento = CpfCnpj(CNPJ_VALIDO)

    assert documento.value == "11222333000181"
    assert documento.is_cpf is False
    assert documento.tipo == "CNPJ"


def test_igualdade_por_valor():
    """Testa que dois documentos com os mesmos dígitos são o mesmo valor."""

    com_mascara = CpfCnpj(CPF_VALIDO)
    sem_mascara = CpfCnpj("52998224725")

    assert com_mascara == sem_mascara
    assert hash(com_mascara) == hash(sem_mascara)
    assert len({com_mascara, sem_mascara}) == 1


def test_documentos_diferentes_nao_sao_iguais():
    """Testa que documentos distintos não colidem."""

    assert CpfCnpj(CPF_VALIDO) != CpfCnpj(CNPJ_VALIDO)


def test_e_imutavel():
    """Testa que o valor não pode ser alterado após a criação."""

    documento = CpfCnpj(CPF_VALIDO)

    with pytest.raises(dataclasses.FrozenInstanceError):
        documento.value = "11222333000181"


def test_formatacao_de_cpf():
    """Testa a máscara de exibição do CPF."""

    assert CpfCnpj("52998224725").formatado() == "529.982.247-25"


def test_formatacao_de_cnpj():
    """Testa a máscara de exibição do CNPJ."""

    assert CpfCnpj("11222333000181").formatado() == "11.222.333/0001-81"


@pytest.mark.parametrize("documento", ["", "   ", None])
def test_documento_obrigatorio(documento):
    """Testa que o value object não aceita vazio."""

    with pytest.raises(ValueError, match="deve ser preenchido"):
        CpfCnpj(documento)


@pytest.mark.parametrize("documento", ["123", "1234567890", "123456789012345"])
def test_quantidade_invalida_de_digitos(documento):
    """Testa a rejeição de documentos fora de 11 ou 14 dígitos."""

    with pytest.raises(ValueError, match="11 dígitos"):
        CpfCnpj(documento)


@pytest.mark.parametrize("documento", ["111.111.111-11", "00000000000000"])
def test_digitos_repetidos(documento):
    """Testa a rejeição de sequências repetidas."""

    with pytest.raises(ValueError, match="inválido"):
        CpfCnpj(documento)


@pytest.mark.parametrize(
    "documento",
    ["52998224724", "52998224715", "12345678900"],
)
def test_cpf_com_digito_verificador_invalido(documento):
    """Testa a rejeição de CPF que passa no tamanho mas falha no cálculo."""

    with pytest.raises(ValueError, match="inválido"):
        CpfCnpj(documento)


@pytest.mark.parametrize(
    "documento",
    ["11222333000182", "11222333000191", "12345678000100"],
)
def test_cnpj_com_digito_verificador_invalido(documento):
    """Testa a rejeição de CNPJ que passa no tamanho mas falha no cálculo."""

    with pytest.raises(ValueError, match="inválido"):
        CpfCnpj(documento)

def test_cria_cnpj_alfanumerico_valido():
    documento = CpfCnpj("12.ABC.345/01DE-35")

    assert documento.value == "12ABC34501DE35"
    assert documento.is_cpf is False
    assert documento.tipo == "CNPJ"


def test_cnpj_alfanumerico_minusculo_e_normalizado():
    documento = CpfCnpj("12.abc.345/01de-35")

    assert documento.value == "12ABC34501DE35"


def test_formatacao_cnpj_alfanumerico():
    documento = CpfCnpj("12ABC34501DE35")

    assert documento.formatado() == "12.ABC.345/01DE-35"


def test_cnpj_alfanumerico_com_dv_invalido():
    with pytest.raises(ValueError, match="inválido"):
        CpfCnpj("12.ABC.345/01DE-36")
