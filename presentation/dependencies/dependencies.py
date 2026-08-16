from fastapi import Depends

from application.commands.login_user import LoginUserUseCase
from application.commands.register_user import RegisterUserUseCase
from application.commands.criar_ordem_servico import CriarOrdemServicoUseCase
from application.queries.get_ordem_servico_detalhada import (
    GetOrdemServicoDetalhadaUseCase,
)
from application.queries.list_ordens_servico import ListOrdensServicoUseCase
from infrastructure.auth.password_hasher import BCryptPasswordHasher
from infrastructure.database.database import get_db
from infrastructure.database.repositories.cliente_repository_impl import (
    ClienteRepositoryImpl,
)
from infrastructure.database.repositories.insumo_repository_impl import (
    InsumoRepositoryImpl,
)
from infrastructure.database.repositories.servico_repository_impl import (
    ServicoRepositoryImpl,
)
from infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from infrastructure.database.repositories.veiculo_repository_impl import (
    VeiculoRepositoryImpl,
)
from infrastructure.database.repositories.ordem_servico_repository_impl import (
    OrdemServicoRepositoryImpl,
)


def get_register_user_use_case(
    db=Depends(get_db),
) -> RegisterUserUseCase:
    """Factory para injeção de dependências do caso de uso."""

    repository = UserRepositoryImpl(db)
    password_hasher = BCryptPasswordHasher()

    return RegisterUserUseCase(
        user_repository=repository,
        password_hasher=password_hasher,
    )


def get_login_user_use_case(
    db=Depends(get_db),
) -> LoginUserUseCase:
    """Factory para injeção de dependências do caso de uso de login."""

    repository = UserRepositoryImpl(db)
    password_hasher = BCryptPasswordHasher()

    return LoginUserUseCase(
        user_repository=repository,
        password_hasher=password_hasher,
    )


def get_criar_ordem_servico_use_case(
    db=Depends(get_db),
) -> CriarOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de criar OS."""
    
    repository = OrdemServicoRepositoryImpl(db)
    
    return CriarOrdemServicoUseCase(
        ordem_servico_repository=repository,
        db=db,
    )


def get_list_ordens_servico_use_case(
    db=Depends(get_db),
) -> ListOrdensServicoUseCase:
    """Factory para injeção de dependências do caso de uso de listagem de OS."""

    return ListOrdensServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
    )


def get_ordem_servico_detalhada_use_case(
    db=Depends(get_db),
) -> GetOrdemServicoDetalhadaUseCase:
    """Factory para injeção de dependências do caso de uso de detalhe de OS."""

    return GetOrdemServicoDetalhadaUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
        veiculo_repository=VeiculoRepositoryImpl(db),
        cliente_repository=ClienteRepositoryImpl(db),
        servico_repository=ServicoRepositoryImpl(db),
        insumo_repository=InsumoRepositoryImpl(db),
    )