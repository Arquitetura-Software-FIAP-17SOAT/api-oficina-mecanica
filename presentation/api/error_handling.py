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


def ordem_servico_ou_404(ordem_servico: Optional[T], ordem_id: int) -> T:
    if ordem_servico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ordem de serviço {ordem_id} não encontrada",
        )
    return ordem_servico
