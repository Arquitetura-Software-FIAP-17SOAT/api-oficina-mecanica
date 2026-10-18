from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Porta para agrupar escritas em uma única transação.

    Usada como ``async with unit_of_work:``: se o bloco terminar sem erro as
    alterações dos repositórios são confirmadas juntas; se levantar exceção,
    todas são descartadas.
    """

    async def __aenter__(self) -> "UnitOfWork":
        self.iniciar()
        return self

    async def __aexit__(self, tipo_excecao, excecao, traceback) -> bool:
        if tipo_excecao is None:
            self.confirmar()
        else:
            self.desfazer()
        return False

    @abstractmethod
    def iniciar(self) -> None:
        pass

    @abstractmethod
    def confirmar(self) -> None:
        pass

    @abstractmethod
    def desfazer(self) -> None:
        pass
