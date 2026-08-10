from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

DOIS_DIGITOS = Decimal("0.01")
VALOR_MAXIMO = Decimal("99999999.99")


@dataclass(frozen=True, order=True)
class Dinheiro:
    """Valor monetário com duas casas decimais."""

    value: Decimal

    def __post_init__(self):
        object.__setattr__(self, "value", self._validar(self.value))

    @staticmethod
    def _validar(valor) -> Decimal:
        if valor is None:
            raise ValueError("O valor deve ser preenchido.")

        if isinstance(valor, Dinheiro):
            return valor.value

        try:
            decimal = Decimal(str(valor))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("O valor informado não é um número válido.")

        if decimal.is_nan() or decimal.is_infinite():
            raise ValueError("O valor informado não é um número válido.")

        if decimal < 0:
            raise ValueError("O valor não pode ser negativo.")

        if decimal > VALOR_MAXIMO:
            raise ValueError(f"O valor não pode ultrapassar {VALOR_MAXIMO}.")

        return decimal.quantize(DOIS_DIGITOS, rounding=ROUND_HALF_UP)

    @classmethod
    def zero(cls) -> "Dinheiro":
        return cls(Decimal("0"))

    def __add__(self, outro: "Dinheiro") -> "Dinheiro":
        if not isinstance(outro, Dinheiro):
            return NotImplemented

        return Dinheiro(self.value + outro.value)

    def __sub__(self, outro: "Dinheiro") -> "Dinheiro":
        if not isinstance(outro, Dinheiro):
            return NotImplemented

        return Dinheiro(self.value - outro.value)

    def __mul__(self, quantidade) -> "Dinheiro":
        if isinstance(quantidade, bool) or not isinstance(
            quantidade, (int, Decimal)
        ):
            return NotImplemented

        return Dinheiro(self.value * Decimal(str(quantidade)))

    __rmul__ = __mul__

    @property
    def is_zero(self) -> bool:
        return self.value == 0

    def formatado(self) -> str:
        inteiro, centavos = f"{self.value:.2f}".split(".")

        milhares = ""
        while len(inteiro) > 3:
            milhares = f".{inteiro[-3:]}{milhares}"
            inteiro = inteiro[:-3]

        return f"R$ {inteiro}{milhares},{centavos}"

    def __str__(self) -> str:
        return f"{self.value:.2f}"
