import re
from dataclasses import dataclass

EMAIL_MAX_LENGTH = 150
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$")


@dataclass(frozen=True, order=True)
class Email:
    """Endereço de e-mail normalizado."""

    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", self._validar(self.value))

    @staticmethod
    def _validar(email) -> str:
        if email is None:
            raise ValueError("O e-mail deve ser preenchido.")

        if isinstance(email, Email):
            return email.value

        if not isinstance(email, str):
            raise ValueError("E-mail inválido.")

        email = email.strip().lower()

        if not email:
            raise ValueError("O e-mail deve ser preenchido.")

        if len(email) > EMAIL_MAX_LENGTH:
            raise ValueError(
                "O e-mail deve possuir no máximo "
                f"{EMAIL_MAX_LENGTH} caracteres."
            )

        if not EMAIL_REGEX.match(email):
            raise ValueError("E-mail inválido.")

        return email

    @property
    def local(self) -> str:
        return self.value.split("@")[0]

    @property
    def dominio(self) -> str:
        return self.value.split("@")[1]

    def __str__(self) -> str:
        return self.value
