from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserUseCase,
)
from presentation.dependencies.dependencies import (
    get_register_user_use_case,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class RegisterUserResponse(BaseModel):
    user_id: int
    message: str


@router.post(
    "/register",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    request: RegisterUserRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    try:
        command = RegisterUserCommand(
            name=request.name,
            email=request.email,
            password=request.password,
        )

        user = await use_case.execute(command)

        return RegisterUserResponse(
            user_id=user.id,
            message="Usuário cadastrado com sucesso.",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )