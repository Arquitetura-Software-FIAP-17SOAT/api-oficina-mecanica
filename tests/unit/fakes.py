from application.ports.unit_of_work import UnitOfWork


class UnitOfWorkFalso(UnitOfWork):
    """Unidade de trabalho em memória, que registra como o bloco terminou."""

    def __init__(self):
        self.iniciada = 0
        self.confirmada = 0
        self.desfeita = 0

    def iniciar(self) -> None:
        self.iniciada += 1

    def confirmar(self) -> None:
        self.confirmada += 1

    def desfazer(self) -> None:
        self.desfeita += 1
