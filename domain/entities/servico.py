from decimal import Decimal

from domain.value_objects.dinheiro import Dinheiro


class Servico:
    NOME_MAX_LENGTH = 100
    TEMPO_ESTIMADO_MAX_LENGTH = 30

    def __init__(
        self,
        nome: str,
        valor: Dinheiro | Decimal | str | float,
        descricao: str | None = None,
        tempo_estimado: str | None = None,
        id: int | None = None,
    ):
        self.id = id
        self.nome = self._validar_nome(nome)
        self.valor = Dinheiro(valor)
        self.descricao = descricao.strip() if descricao else None
        self.tempo_estimado = self._validar_tempo_estimado(tempo_estimado)

    @classmethod
    def _validar_nome(cls, nome: str) -> str:
        if not nome or not nome.strip():
            raise ValueError("O nome do serviço deve ser preenchido.")

        nome = nome.strip()

        if len(nome) > cls.NOME_MAX_LENGTH:
            raise ValueError(
                "O nome do serviço deve possuir no máximo "
                f"{cls.NOME_MAX_LENGTH} caracteres."
            )

        return nome

    @classmethod
    def _validar_tempo_estimado(cls, tempo_estimado: str | None) -> str | None:
        if not tempo_estimado or not tempo_estimado.strip():
            return None

        tempo_estimado = tempo_estimado.strip()

        if len(tempo_estimado) > cls.TEMPO_ESTIMADO_MAX_LENGTH:
            raise ValueError(
                "O tempo estimado deve possuir no máximo "
                f"{cls.TEMPO_ESTIMADO_MAX_LENGTH} caracteres."
            )

        return tempo_estimado

    def change_nome(self, nome: str) -> None:
        self.nome = self._validar_nome(nome)

    def change_valor(self, valor: Dinheiro | Decimal | str | float) -> None:
        self.valor = Dinheiro(valor)

    def change_descricao(self, descricao: str | None) -> None:
        self.descricao = descricao.strip() if descricao else None

    def change_tempo_estimado(self, tempo_estimado: str | None) -> None:
        self.tempo_estimado = self._validar_tempo_estimado(tempo_estimado)
