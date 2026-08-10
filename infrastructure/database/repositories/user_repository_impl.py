from sqlalchemy.orm import Session

from domain.entities.usuario import Usuario
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel


class UserRepositoryImpl(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    async def save(self, user: Usuario) -> Usuario:
        model = UserModel(
            nome=user.name,
            email=user.email,
            telefone=None,
            senha_hash=user.hashed_password,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        user.id = model.id

        return user

    async def find_by_email(self, email: str):
        model = (
            self.db.query(UserModel)
            .filter(UserModel.email == email)
            .first()
        )

        if model is None:
            return None

        return Usuario(
            name=model.nome,
            email=model.email,
            hashed_password=model.senha_hash,
        )

    async def exists_by_email(self, email: str) -> bool:
        return (
            self.db.query(UserModel)
            .filter(UserModel.email == email)
            .first()
            is not None
<<<<<<< HEAD
        )
=======
        )

    async def find_by_id(self, user_id: int):
        model = self.db.get(UserModel, user_id)

        if model is None:
            return None

        user = User(
            name=model.nome,
            email=model.email,
            hashed_password=model.senha_hash,
        )
        user.id = model.id

        return user

    async def list(self):
        raise NotImplementedError()

    async def update(self, user: User):
        raise NotImplementedError()

    async def delete(self, user_id: int):
        raise NotImplementedError()
>>>>>>> e34f6833ad6ee07e6523ec044f79028d2c4f41f3
