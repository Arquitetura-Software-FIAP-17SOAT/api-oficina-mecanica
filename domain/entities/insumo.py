from decimal import Decimal

from domain.value_objects.dinheiro import Dinheiro


class Insumo:
    NOME_MAX_LENGTH = 120

    def __init__(
        self,
        nome: str,
        descricao: str | None = None,
        preco_unitario: Dinheiro | Decimal | str | float | None = None,
        estoque: int = 0,
        quantidade_minima: int = 0,
        id: int | None = None,
    ):
        self.id = id
        self.nome = self._validar_nome(nome)
        self.descricao = descricao.strip() if descricao else None
        self.preco_unitario = self._validar_preco(preco_unitario)
        self.estoque = self._validar_quantidade(estoque, "O estoque")
        self.quantidade_minima = self._validar_quantidade(
            quantidade_minima, "A quantidade mínima"
        )

    # ------------------------------------------------------------------
    # Validações
    # ------------------------------------------------------------------

    @classmethod
    def _validar_nome(cls, nome: str) -> str:
        if not nome or not nome.strip():
            raise ValueError("O nome do insumo deve ser preenchido.")

        nome = nome.strip()

        if len(nome) > cls.NOME_MAX_LENGTH:
            raise ValueError(
                "O nome do insumo deve possuir no máximo "
                f"{cls.NOME_MAX_LENGTH} caracteres."
            )

        return nome

    @staticmethod
    def _validar_preco(preco) -> Dinheiro | None:
        if preco is None:
            return None

        return Dinheiro(preco)

    @staticmethod
    def _validar_quantidade(quantidade: int, rotulo: str) -> int:
        if not isinstance(quantidade, int) or isinstance(quantidade, bool):
            raise ValueError(f"{rotulo} deve ser um número inteiro.")

        if quantidade < 0:
            raise ValueError(f"{rotulo} não pode ser negativo.")

        return quantidade

    @staticmethod
    def _validar_movimentacao(quantidade: int) -> int:
        if not isinstance(quantidade, int) or isinstance(quantidade, bool):
            raise ValueError("A quantidade deve ser um número inteiro.")

        if quantidade <= 0:
            raise ValueError("A quantidade movimentada deve ser maior que zero.")

        return quantidade

    # Cadastro
    def change_nome(self, nome: str) -> None:
        self.nome = self._validar_nome(nome)

    def change_descricao(self, descricao: str | None) -> None:
        self.descricao = descricao.strip() if descricao else None

    def change_preco_unitario(self, preco_unitario=None) -> None:
        self.preco_unitario = self._validar_preco(preco_unitario)

    def change_quantidade_minima(self, quantidade_minima: int) -> None:
        self.quantidade_minima = self._validar_quantidade(
            quantidade_minima, "A quantidade mínima"
        )

    # ------------------------------------------------------------------
    # Controle de estoque
    # ------------------------------------------------------------------

    def adicionar_estoque(self, quantidade: int) -> None:
        """Entrada de estoque (compra, devolução)."""
        self.estoque += self._validar_movimentacao(quantidade)

    def remover_estoque(self, quantidade: int) -> None:
        """Saída de estoque (consumo em serviço, perda)."""
        quantidade = self._validar_movimentacao(quantidade)

        if quantidade > self.estoque:
            raise ValueError(
                f"Estoque insuficiente para '{self.nome}': "
                f"disponível {self.estoque}, solicitado {quantidade}."
            )

        self.estoque -= quantidade

    def ajustar_estoque(self, quantidade: int) -> None:
        """Define o saldo absoluto (inventário/contagem)."""
        self.estoque = self._validar_quantidade(quantidade, "O estoque")

    @property
    def estoque_baixo(self) -> bool:
        """Indica que o saldo atingiu ou ficou abaixo do mínimo."""
        return self.estoque <= self.quantidade_minima
