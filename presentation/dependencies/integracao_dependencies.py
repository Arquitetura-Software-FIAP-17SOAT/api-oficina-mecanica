import hmac

from fastapi import Header, HTTPException, status

from infrastructure.config.config import settings


def validar_chave_integracao(
    x_api_key: str | None = Header(
        None,
        description="Chave de API do sistema externo que notifica a oficina.",
    ),
) -> None:
    """Autentica sistemas externos (ex.: app do cliente, provedor de e-mail).

    Eles não têm um usuário/JWT de funcionário, então apresentam uma chave
    compartilhada no header ``X-API-Key``. Sem ``INTEGRACAO_API_KEY``
    configurada a integração fica desligada (503), em vez de aceitar qualquer
    chamada.
    """
    chave_configurada = settings.INTEGRACAO_API_KEY

    if not chave_configurada:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Integração externa não configurada.",
        )

    if x_api_key is None or not hmac.compare_digest(x_api_key, chave_configurada):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API inválida.",
        )
