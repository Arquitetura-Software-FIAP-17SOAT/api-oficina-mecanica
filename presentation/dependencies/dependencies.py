from fastapi import Depends

from application.commands.login_user import LoginUserUseCase
from application.commands.register_user import RegisterUserUseCase
from application.commands.criar_ordem_servico import CriarOrdemServicoUseCase
from application.commands.adicionar_item_ordem_servico import (
    AdicionarItemOrdemServicoUseCase,
)
from application.commands.remover_item_ordem_servico import (
    RemoverItemOrdemServicoUseCase,
)
from application.commands.adicionar_insumo_ordem_servico import (
    AdicionarInsumoOrdemServicoUseCase,
)
from application.commands.remover_insumo_ordem_servico import (
    RemoverInsumoOrdemServicoUseCase,
)
from application.commands.iniciar_diagnostico_ordem_servico import (
    IniciarDiagnosticoOrdemServicoUseCase,
)
from application.commands.enviar_ordem_servico_para_aprovacao import (
    EnviarOrdemServicoParaAprovacaoUseCase,
)
from application.commands.aprovar_orcamento_ordem_servico import (
    AprovarOrcamentoOrdemServicoUseCase,
)
from application.commands.rejeitar_orcamento_ordem_servico import (
    RejeitarOrcamentoOrdemServicoUseCase,
)
from application.commands.finalizar_ordem_servico import (
    FinalizarOrdemServicoUseCase,
)
from application.commands.entregar_ordem_servico import EntregarOrdemServicoUseCase
from application.commands.retornar_ordem_servico_para_diagnostico import (
    RetornarOrdemServicoParaDiagnosticoUseCase,
)
from application.commands.iniciar_execucao_servico import (
    IniciarExecucaoServicoUseCase,
)
from application.commands.finalizar_execucao_servico import (
    FinalizarExecucaoServicoUseCase,
)
from application.queries.consultar_ordem_servico_publica import (
    ConsultarOrdemServicoPublicaUseCase,
)
from application.queries.get_ordem_servico_detalhada import (
    GetOrdemServicoDetalhadaUseCase,
)
from application.queries.list_ordens_servico import ListOrdensServicoUseCase
from application.queries.list_tempo_medio_execucao import (
    ListTempoMedioExecucaoUseCase,
)
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


def get_adicionar_item_ordem_servico_use_case(
    db=Depends(get_db),
) -> AdicionarItemOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de adicionar item à OS."""

    return AdicionarItemOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
        servico_repository=ServicoRepositoryImpl(db),
    )


def get_remover_item_ordem_servico_use_case(
    db=Depends(get_db),
) -> RemoverItemOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de remover item da OS."""

    return RemoverItemOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
    )


def get_adicionar_insumo_ordem_servico_use_case(
    db=Depends(get_db),
) -> AdicionarInsumoOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de adicionar insumo à OS."""

    return AdicionarInsumoOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
        insumo_repository=InsumoRepositoryImpl(db),
    )


def get_remover_insumo_ordem_servico_use_case(
    db=Depends(get_db),
) -> RemoverInsumoOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de remover insumo da OS."""

    return RemoverInsumoOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
        insumo_repository=InsumoRepositoryImpl(db),
    )


def get_iniciar_diagnostico_use_case(
    db=Depends(get_db),
) -> IniciarDiagnosticoOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de diagnóstico."""

    return IniciarDiagnosticoOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
    )


def get_enviar_ordem_servico_para_aprovacao_use_case(
    db=Depends(get_db),
) -> EnviarOrdemServicoParaAprovacaoUseCase:
    """Factory para injeção de dependências do caso de uso de envio para aprovação."""

    return EnviarOrdemServicoParaAprovacaoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
    )


def get_aprovar_orcamento_use_case(
    db=Depends(get_db),
) -> AprovarOrcamentoOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de aprovação do orçamento."""

    return AprovarOrcamentoOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
    )


def get_rejeitar_orcamento_use_case(
    db=Depends(get_db),
) -> RejeitarOrcamentoOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de rejeição."""

    return RejeitarOrcamentoOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
    )


def get_finalizar_ordem_servico_use_case(
    db=Depends(get_db),
) -> FinalizarOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de finalização de OS."""

    return FinalizarOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
    )


def get_entregar_ordem_servico_use_case(
    db=Depends(get_db),
) -> EntregarOrdemServicoUseCase:
    """Factory para injeção de dependências do caso de uso de entrega de OS."""

    return EntregarOrdemServicoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
    )


def get_retornar_ordem_servico_para_diagnostico_use_case(
    db=Depends(get_db),
) -> RetornarOrdemServicoParaDiagnosticoUseCase:
    """Factory para injeção de dependências do caso de uso de retorno ao diagnóstico."""

    return RetornarOrdemServicoParaDiagnosticoUseCase(
        ordem_servico_repository=OrdemServicoRepositoryImpl(db),
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


def get_consultar_ordem_servico_publica_use_case(
    db=Depends(get_db),
) -> ConsultarOrdemServicoPublicaUseCase:
    """Factory do caso de uso de acompanhamento da OS pelo cliente."""

    return ConsultarOrdemServicoPublicaUseCase(
        get_ordem_servico_detalhada_use_case=get_ordem_servico_detalhada_use_case(db),
    )


def get_list_tempo_medio_execucao_use_case(
    db=Depends(get_db),
) -> ListTempoMedioExecucaoUseCase:
    """Factory do caso de uso de consulta do tempo médio de execução por serviço."""

    return ListTempoMedioExecucaoUseCase(
        servico_repository=ServicoRepositoryImpl(db),
    )


def get_iniciar_execucao_servico_use_case(
    db=Depends(get_db),
) -> IniciarExecucaoServicoUseCase:
    """Factory para injeção de dependências do caso de uso de início de execução de serviço."""

    return IniciarExecucaoServicoUseCase(db=db)


def get_finalizar_execucao_servico_use_case(
    db=Depends(get_db),
) -> FinalizarExecucaoServicoUseCase:
    """Factory para injeção de dependências do caso de uso de fim de execução de serviço."""

    return FinalizarExecucaoServicoUseCase(db=db)
