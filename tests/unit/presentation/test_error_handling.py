import pytest
from fastapi import HTTPException

from presentation.api.error_handling import ordem_servico_ou_404, traduzir_erros


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
