from datetime import datetime

import pytest

from domain.entities.veiculo import Veiculo


def criar_veiculo(**kwargs) -> Veiculo:
    padrao = {
        "cliente_id": 1,
        "marca_id": 2,
        "placa": "ABC1234",
        "modelo": "Gol 1.0",
        "ano_fabricacao": 2020,
    }
    padrao.update(kwargs)

    return Veiculo(**padrao)


def test_cria_veiculo_valido():
    """Testa a criação de um veículo com dados válidos."""

    veiculo = criar_veiculo()

    assert veiculo.id is None
    assert veiculo.cliente_id == 1
    assert veiculo.marca_id == 2
    assert str(veiculo.placa) == "ABC1234"
    assert veiculo.modelo == "Gol 1.0"


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("abc1234", "ABC1234"),
        ("ABC-1234", "ABC1234"),
        ("abc 1d23", "ABC1D23"),
        ("ABC1D23", "ABC1D23"),
    ],
)
def test_placa_e_normalizada(entrada, esperado):
    """Testa a normalização de placas antigas e Mercosul."""

    veiculo = criar_veiculo(placa=entrada)

    assert str(veiculo.placa) == esperado


@pytest.mark.parametrize("placa", ["ABCD123", "1234ABC", "ABCDEFG"])
def test_placa_em_formato_invalido(placa):
    """Testa a rejeição de placas com 7 caracteres fora dos padrões válidos."""

    with pytest.raises(ValueError, match="formato ABC1234"):
        criar_veiculo(placa=placa)


@pytest.mark.parametrize("placa", ["AB1234", "ABC12345"])
def test_placa_com_quantidade_de_caracteres_invalida(placa):
    """Testa a rejeição de placas que não têm exatamente 7 caracteres."""

    with pytest.raises(ValueError, match="exatamente 7 caracteres"):
        criar_veiculo(placa=placa)


@pytest.mark.parametrize("placa", ["", "   ", None])
def test_placa_obrigatoria(placa):
    """Testa que o veículo não pode ser criado sem placa."""

    with pytest.raises(ValueError, match="deve ser preenchida"):
        criar_veiculo(placa=placa)


@pytest.mark.parametrize("modelo", ["", "   ", None])
def test_modelo_obrigatorio(modelo):
    """Testa que o veículo não pode ser criado sem modelo."""

    with pytest.raises(ValueError, match="deve ser preenchido"):
        criar_veiculo(modelo=modelo)


def test_modelo_com_tamanho_excedido():
    """Testa o limite de 100 caracteres do modelo, imposto pela coluna."""

    with pytest.raises(ValueError, match="no máximo 100 caracteres"):
        criar_veiculo(modelo="a" * 101)


def test_chassi_opcional_e_normalizado():
    """Testa que o chassi é opcional e vai para maiúsculas."""

    assert criar_veiculo(chassi=None).chassi is None
    assert str(criar_veiculo(chassi=" 9bwzzz377vt004251 ").chassi) == (
        "9BWZZZ377VT004251"
    )


def test_chassi_com_tamanho_invalido():
    """Testa que o chassi precisa ter exatamente 17 caracteres."""

    with pytest.raises(ValueError, match="exatamente 17 caracteres"):
        criar_veiculo(chassi="a" * 18)


def test_ano_fabricacao_opcional():
    """Testa que o ano de fabricação pode ficar em branco."""

    assert criar_veiculo(ano_fabricacao=None).ano_fabricacao is None


def test_ano_fabricacao_aceita_modelo_do_ano_seguinte():
    """Testa que a montadora pode lançar o modelo do ano que vem."""

    ano_seguinte = datetime.now().year + 1

    veiculo = criar_veiculo(ano_fabricacao=ano_seguinte)

    assert veiculo.ano_fabricacao == ano_seguinte


@pytest.mark.parametrize("ano", [1899, 2087])
def test_ano_fabricacao_fora_da_faixa(ano):
    """Testa a rejeição de anos implausíveis."""

    with pytest.raises(ValueError, match="ano de fabricação deve estar entre"):
        criar_veiculo(ano_fabricacao=ano)


@pytest.mark.parametrize("cliente_id", [0, -1, None])
def test_cliente_obrigatorio(cliente_id):
    """Testa que o veículo exige um cliente válido."""

    with pytest.raises(ValueError):
        criar_veiculo(cliente_id=cliente_id)


@pytest.mark.parametrize("marca_id", [0, -1, None])
def test_marca_obrigatoria(marca_id):
    """Testa que o veículo exige uma marca válida."""

    with pytest.raises(ValueError):
        criar_veiculo(marca_id=marca_id)


def test_chassi_como_string_vazia_e_tratado_como_none():
    """Testa que uma string vazia de chassi equivale a não informar."""

    veiculo = criar_veiculo(chassi="   ")

    assert veiculo.chassi is None


def test_ano_fabricacao_nao_inteiro_e_invalido():
    """Testa que o ano de fabricação deve ser um número inteiro."""

    with pytest.raises(ValueError, match="número inteiro"):
        criar_veiculo(ano_fabricacao=2020.5)


def test_change_placa():
    """Testa a alteração da placa do veículo."""

    veiculo = criar_veiculo()
    veiculo.change_placa("XYZ9A87")

    assert str(veiculo.placa) == "XYZ9A87"


def test_change_modelo():
    """Testa a alteração do modelo do veículo."""

    veiculo = criar_veiculo()
    veiculo.change_modelo("Gol 1.6")

    assert veiculo.modelo == "Gol 1.6"


def test_change_chassi():
    """Testa a alteração do chassi do veículo."""

    veiculo = criar_veiculo(chassi=None)
    veiculo.change_chassi("9BWZZZ377VT004251")

    assert str(veiculo.chassi) == "9BWZZZ377VT004251"

    veiculo.change_chassi(None)
    assert veiculo.chassi is None


def test_change_ano_fabricacao():
    """Testa a alteração do ano de fabricação do veículo."""

    veiculo = criar_veiculo()
    veiculo.change_ano_fabricacao(2022)

    assert veiculo.ano_fabricacao == 2022


def test_change_marca():
    """Testa a alteração da marca do veículo."""

    veiculo = criar_veiculo()
    veiculo.change_marca(5)

    assert veiculo.marca_id == 5
