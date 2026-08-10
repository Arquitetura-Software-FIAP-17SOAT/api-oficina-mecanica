from domain.value_objects.cpf_cnpj import CpfCnpj
from domain.value_objects.email import Email


class Cliente:
    NOME_MAX_LENGTH = 150

    def __init__(
        self,
        nome: str,
        usuario_id: int,
        cpf_cnpj: str | CpfCnpj | None = None,
        email: str | Email | None = None,
        id: int | None = None,
    ):
        self.id = id
        self.usuario_id = self._validar_usuario_id(usuario_id)
        self.nome = self._validar_nome(nome)
        self.cpf_cnpj = self._validar_cpf_cnpj(cpf_cnpj)
        self.email = self._validar_email(email)

    @staticmethod
    def _validar_usuario_id(usuario_id: int) -> int:
        if not isinstance(usuario_id, int) or isinstance(usuario_id, bool):
            raise ValueError("O usuário responsável deve ser informado.")

        if usuario_id <= 0:
            raise ValueError("O usuário responsável é inválido.")

        return usuario_id

    @classmethod
    def _validar_nome(cls, nome: str) -> str:
        if not nome or not nome.strip():
            raise ValueError("O nome do cliente deve ser preenchido.")

        nome = nome.strip()

        if len(nome) > cls.NOME_MAX_LENGTH:
            raise ValueError(
                "O nome do cliente deve possuir no máximo "
                f"{cls.NOME_MAX_LENGTH} caracteres."
            )

        return nome

    @staticmethod
    def _validar_cpf_cnpj(cpf_cnpj: str | CpfCnpj | None) -> CpfCnpj | None:
        if cpf_cnpj is None:
            return None

        if isinstance(cpf_cnpj, CpfCnpj):
            return cpf_cnpj

        if not str(cpf_cnpj).strip():
            return None

        return CpfCnpj(cpf_cnpj)

    @staticmethod
    def _validar_email(email: str | Email | None) -> Email | None:
        if email is None:
            return None

        if isinstance(email, str) and not email.strip():
            return None

        return Email(email)

    def change_nome(self, nome: str) -> None:
        self.nome = self._validar_nome(nome)

    def change_cpf_cnpj(self, cpf_cnpj: str | CpfCnpj | None) -> None:
        self.cpf_cnpj = self._validar_cpf_cnpj(cpf_cnpj)

    def change_email(self, email: str | Email | None) -> None:
        self.email = self._validar_email(email)
