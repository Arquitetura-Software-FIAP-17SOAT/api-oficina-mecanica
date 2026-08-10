import re
from dataclasses import dataclass

CPF_LENGTH = 11
CNPJ_LENGTH = 14

CNPJ_PESOS_PRIMEIRO_DIGITO = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
CNPJ_PESOS_SEGUNDO_DIGITO = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


@dataclass(frozen=True)
class CpfCnpj:
    """Documento de um cliente, guardado apenas com os dígitos."""

    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", self._validar(self.value))

    @classmethod
    def _validar(cls, documento: str) -> str:
        if not documento or not str(documento).strip():
            raise ValueError("O CPF/CNPJ deve ser preenchido.")

        digitos = re.sub(r"\D", "", str(documento))

        if len(digitos) not in (CPF_LENGTH, CNPJ_LENGTH):
            raise ValueError(
                "O CPF deve possuir 11 dígitos e o CNPJ 14 dígitos."
            )

        if digitos == digitos[0] * len(digitos):
            raise ValueError("O CPF/CNPJ informado é inválido.")

        valido = (
            cls._cpf_valido(digitos)
            if len(digitos) == CPF_LENGTH
            else cls._cnpj_valido(digitos)
        )

        if not valido:
            raise ValueError("O CPF/CNPJ informado é inválido.")

        return digitos

    @staticmethod
    def _digito_verificador(soma: int) -> str:
        resto = soma % 11

        return "0" if resto < 2 else str(11 - resto)

    @classmethod
    def _cpf_valido(cls, digitos: str) -> bool:
        primeiro = cls._digito_verificador(
            sum(int(digitos[i]) * (10 - i) for i in range(9))
        )

        if digitos[9] != primeiro:
            return False

        segundo = cls._digito_verificador(
            sum(int(digitos[i]) * (11 - i) for i in range(10))
        )

        return digitos[10] == segundo

    @classmethod
    def _cnpj_valido(cls, digitos: str) -> bool:
        primeiro = cls._digito_verificador(
            sum(
                int(digito) * peso
                for digito, peso in zip(digitos, CNPJ_PESOS_PRIMEIRO_DIGITO)
            )
        )

        if digitos[12] != primeiro:
            return False

        segundo = cls._digito_verificador(
            sum(
                int(digito) * peso
                for digito, peso in zip(digitos, CNPJ_PESOS_SEGUNDO_DIGITO)
            )
        )

        return digitos[13] == segundo

    @property
    def is_cpf(self) -> bool:
        return len(self.value) == CPF_LENGTH

    @property
    def tipo(self) -> str:
        return "CPF" if self.is_cpf else "CNPJ"

    def formatado(self) -> str:
        if self.is_cpf:
            return (
                f"{self.value[:3]}.{self.value[3:6]}.{self.value[6:9]}"
                f"-{self.value[9:]}"
            )

        return (
            f"{self.value[:2]}.{self.value[2:5]}.{self.value[5:8]}"
            f"/{self.value[8:12]}-{self.value[12:]}"
        )

    def __str__(self) -> str:
        return self.value
