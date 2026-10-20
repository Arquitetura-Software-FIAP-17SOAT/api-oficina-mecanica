from contextlib import contextmanager
from typing import Iterator, Optional, TypeVar

from fastapi import HTTPException, status

T = TypeVar("T")


@contextmanager
def traduzir_erros(
    mensagem_erro_interno: str,
    nao_encontrado: tuple[type[Exception], ...] = (),
) -> Iterator[None]:
    """Traduz exceções da camada de aplicação para respostas HTTP.

    - ``HTTPException``: repassada sem alteração.
    - Exceções em ``nao_encontrado``: 404.
    - ``ValueError`` (regra de negócio violada): 400.
    - Qualquer outra: 500 com ``mensagem_erro_interno``.
    """
    try:
        yield
    except HTTPException:
        raise
    except nao_encontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=mensagem_erro_interno,
        )


@contextmanager
def traduzir_value_error(
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Iterator[None]:
    """Traduz ``ValueError`` (regra de negócio violada) em resposta HTTP.

    Versão enxuta de ``traduzir_erros``, para as rotas que deixam qualquer
    outra exceção seguir para o tratador padrão do FastAPI.
    """
    try:
        yield
    except ValueError as e:
        raise HTTPException(status_code=status_code, detail=str(e))


def encontrado_ou_404(recurso: Optional[T], mensagem: str) -> T:
    """Devolve o recurso ou responde 404 quando ele não existe (``None``)."""
    if recurso is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=mensagem)
    return recurso


def exclusao_ou_404(excluido: bool, mensagem: str) -> None:
    """Responde 404 quando a exclusão não encontrou o registro."""
    if not excluido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=mensagem)


def ordem_servico_ou_404(ordem_servico: Optional[T], ordem_id: int) -> T:
    return encontrado_ou_404(
        ordem_servico, f"Ordem de serviço {ordem_id} não encontrada"
    )
