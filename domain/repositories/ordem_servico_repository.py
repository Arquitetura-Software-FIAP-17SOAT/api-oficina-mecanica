from abc import ABC, abstractmethod

from domain.entities.ordem_servico import OrdemServico


class OrdemServicoRepository(ABC):
    """Interface (contrato) para o repositório de Ordem de Serviço"""

    @abstractmethod
    async def save(self, ordem_servico: OrdemServico) -> OrdemServico:
        """Salva uma nova ordem de serviço ou atualiza uma existente"""
        pass

    @abstractmethod
    async def find_by_id(self, ordem_servico_id: int) -> OrdemServico | None:
        """Busca uma ordem de serviço pelo ID"""
        pass

    @abstractmethod
    async def find_by_veiculo_id(self, veiculo_id: str) -> list:
        """Busca todas as ordens de serviço de um veículo"""
        pass

    @abstractmethod
    async def find_by_status(self, status: str) -> list:
        """Busca todas as ordens de serviço com um status específico"""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 10) -> list:
        """Lista todas as ordens de serviço com paginação"""
        pass

    @abstractmethod
    async def list_paginado(
        self,
        skip: int = 0,
        limit: int = 10,
        status: str | None = None,
        cpf_cnpj: str | None = None,
        placa: str | None = None,
    ) -> tuple[list, int]:
        """Lista ordens de serviço com paginação e filtros opcionais.

        Filtra por status, pelo CPF/CNPJ (apenas dígitos) do cliente dono do
        veículo e/ou pela placa (normalizada) do veículo.

        Retorna uma tupla ``(itens, total)`` onde ``total`` é a quantidade de
        registros que atendem aos filtros, ignorando a paginação — usado para
        calcular o número de páginas.
        """
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Deleta uma ordem de serviço"""
        pass