from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr

from application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserUseCase,
)
from application.commands.login_user import (
    LoginUserCommand,
    LoginUserUseCase,
)
from presentation.api.error_handling import traduzir_value_error
from presentation.dependencies.dependencies import (
    get_register_user_use_case,
    get_login_user_use_case,
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


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/register",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    request: RegisterUserRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    with traduzir_value_error():
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


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
):
    with traduzir_value_error(status.HTTP_401_UNAUTHORIZED):
        command = LoginUserCommand(
            email=request.email,
            password=request.password,
        )

        token = await use_case.execute(command)

        return LoginResponse(
            access_token=token,
        )
