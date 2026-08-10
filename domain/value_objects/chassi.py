import re
from dataclasses import dataclass

CHASSI_LENGTH = 17
LETRAS_PROIBIDAS = ("I", "O", "Q")
CHASSI_REGEX = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


@dataclass(frozen=True, order=True)
class Chassi:
    """Número de chassi (VIN), com 17 caracteres maiúsculos."""

    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", self._validar(self.value))

    @staticmethod
    def _validar(chassi) -> str:
        if chassi is None:
            raise ValueError("O chassi deve ser preenchido.")

        if isinstance(chassi, Chassi):
            return chassi.value

        if not isinstance(chassi, str):
            raise ValueError("O chassi informado é inválido.")

        chassi = re.sub(r"[^A-Za-z0-9]", "", chassi).upper()

        if not chassi:
            raise ValueError("O chassi deve ser preenchido.")

        if len(chassi) != CHASSI_LENGTH:
            raise ValueError(
                f"O chassi deve possuir exatamente {CHASSI_LENGTH} caracteres."
            )

        if any(letra in chassi for letra in LETRAS_PROIBIDAS):
            raise ValueError(
                "O chassi não pode conter as letras I, O ou Q."
            )

        if not CHASSI_REGEX.match(chassi):
            raise ValueError("O chassi informado é inválido.")

        return chassi

    @property
    def wmi(self) -> str:
        """Identificador mundial do fabricante (3 primeiros caracteres)."""
        return self.value[:3]

    @property
    def vds(self) -> str:
        """Seção descritiva do veículo (caracteres 4 a 9)."""
        return self.value[3:9]

    @property
    def vis(self) -> str:
        """Seção identificadora do veículo (caracteres 10 a 17)."""
        return self.value[9:]

    def __str__(self) -> str:
        return self.value
