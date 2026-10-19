"""Schemas (requests e responses) da API de usuários."""

from pydantic import BaseModel, EmailStr


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
