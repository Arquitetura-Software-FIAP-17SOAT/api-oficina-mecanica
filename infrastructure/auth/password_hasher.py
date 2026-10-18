from passlib.context import CryptContext

from application.ports.password_hasher import PasswordHasher


class BCryptPasswordHasher(PasswordHasher):
    """Implementação utilizando BCrypt."""

    def __init__(self):
        self._pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
        )

    def hash(self, password: str) -> str:
        return self._pwd_context.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        return self._pwd_context.verify(password, hashed_password)