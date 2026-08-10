import re
from dataclasses import dataclass

PLACA_LENGTH = 7
PLACA_REGEX = re.compile(r"^[A-Z]{3}[0-9][0-9A-Z][0-9]{2}$")


@dataclass(frozen=True, order=True)
class Placa:
    """Placa veicular brasileira, sempre com 7 caracteres maiúsculos."""

    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", self._validar(self.value))

    @staticmethod
    def _validar(placa) -> str:
        if placa is None:
            raise ValueError("A placa deve ser preenchida.")

        if isinstance(placa, Placa):
            return placa.value

        if not isinstance(placa, str):
            raise ValueError("A placa informada é inválida.")

        placa = re.sub(r"[^A-Za-z0-9]", "", placa).upper()

        if not placa:
            raise ValueError("A placa deve ser preenchida.")

        if len(placa) != PLACA_LENGTH:
            raise ValueError(
                f"A placa deve possuir exatamente {PLACA_LENGTH} caracteres."
            )

        if not PLACA_REGEX.match(placa):
            raise ValueError(
                "A placa deve estar no formato ABC1234 ou ABC1D23."
            )

        return placa

    @property
    def is_mercosul(self) -> bool:
        """Padrão Mercosul tem letra na quinta posição (ABC1D23)."""
        return self.value[4].isalpha()

    @property
    def padrao(self) -> str:
        return "Mercosul" if self.is_mercosul else "Antigo"

    def formatada(self) -> str:
        if self.is_mercosul:
            return self.value

        return f"{self.value[:3]}-{self.value[3:]}"

    def __str__(self) -> str:
        return self.value
