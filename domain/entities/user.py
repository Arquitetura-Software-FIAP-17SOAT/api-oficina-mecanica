from uuid import uuid4


class User:

    def __init__(
        self,
        name: str,
        email: str,
        hashed_password: str
    ):
        if not name or len(name) > 128:
            raise ValueError(
                "O nome deve ser preenchido e possuir no máximo 128 caracteres."
            )

        if not email or len(email) > 128:
            raise ValueError(
                "O e-mail deve ser preenchido e possuir no máximo 128 caracteres."
            )

        if not hashed_password:
            raise ValueError(
                "A senha é obrigatória."
            )

        self.id = str(uuid4())
        self.name = name
        self.email = email.lower()
        self.hashed_password = hashed_password

    def change_name(self, name: str):
        if not name or len(name) > 128:
            raise ValueError(
                "O nome deve ser preenchido e possuir no máximo 128 caracteres."
            )

        self.name = name

    def change_email(self, email: str):
        if not email or len(email) > 128:
            raise ValueError(
                "O e-mail deve ser preenchido e possuir no máximo 128 caracteres."
            )

        self.email = email.lower()

    def change_password(self, hashed_password: str):
        if not hashed_password:
            raise ValueError(
                "A senha é obrigatória."
            )

        self.hashed_password = hashed_password