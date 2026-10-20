import pytest
from fastapi import HTTPException

from presentation.api.error_handling import (
    encontrado_ou_404,
    exclusao_ou_404,
    ordem_servico_ou_404,
    traduzir_erros,
    traduzir_value_error,
)


class NaoEncontradoError(Exception):
    pass


def _status_e_detalhe(excecao: Exception, **kwargs):
    with pytest.raises(HTTPException) as info:
        with traduzir_erros("Erro interno", **kwargs):
            raise excecao
    return info.value.status_code, info.value.detail


def test_value_error_vira_400_com_a_mensagem_original():
    assert _status_e_detalhe(ValueError("regra violada")) == (400, "regra violada")


def test_excecao_de_nao_encontrado_vira_404():
    resultado = _status_e_detalhe(
        NaoEncontradoError("sumiu"), nao_encontrado=(NaoEncontradoError,)
    )

    assert resultado == (404, "sumiu")


def test_excecao_inesperada_vira_500_sem_vazar_detalhes():
    assert _status_e_detalhe(RuntimeError("senha do banco")) == (500, "Erro interno")


def test_http_exception_e_repassada_sem_alteracao():
    original = HTTPException(status_code=418, detail="bule")

    with pytest.raises(HTTPException) as info:
        with traduzir_erros("Erro interno"):
            raise original

    assert info.value is original


def test_sem_erro_o_bloco_executa_normalmente():
    with traduzir_erros("Erro interno"):
        resultado = 1 + 1

    assert resultado == 2


def test_ordem_servico_ou_404():
    assert ordem_servico_ou_404("os", 1) == "os"

    with pytest.raises(HTTPException) as info:
        ordem_servico_ou_404(None, 7)

    assert info.value.status_code == 404
    assert "7" in info.value.detail


def test_traduzir_value_error_usa_400_por_padrao():
    with pytest.raises(HTTPException) as info:
        with traduzir_value_error():
            raise ValueError("inválido")

    assert (info.value.status_code, info.value.detail) == (400, "inválido")


def test_traduzir_value_error_aceita_outro_status():
    with pytest.raises(HTTPException) as info:
        with traduzir_value_error(401):
            raise ValueError("credenciais")

    assert info.value.status_code == 401


def test_traduzir_value_error_nao_captura_outras_excecoes():
    with pytest.raises(RuntimeError):
        with traduzir_value_error():
            raise RuntimeError("inesperado")


def test_encontrado_ou_404():
    assert encontrado_ou_404("recurso", "não achei") == "recurso"
    assert encontrado_ou_404(0, "não achei") == 0  # só None é "não encontrado"

    with pytest.raises(HTTPException) as info:
        encontrado_ou_404(None, "não achei")

    assert (info.value.status_code, info.value.detail) == (404, "não achei")


def test_exclusao_ou_404():
    assert exclusao_ou_404(True, "não achei") is None

    with pytest.raises(HTTPException) as info:
        exclusao_ou_404(False, "não achei")

    assert info.value.status_code == 404
