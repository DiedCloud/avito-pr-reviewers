from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.controller.schemas.auth import Token, UserCreate
from src.service.auth_service import (
    create_access_token,
    create_user,
    get_user_by_login,
    verify_password,
)


AUTH_ROUTER_PREFIX = "/auth"

auth_router = APIRouter(prefix=AUTH_ROUTER_PREFIX, tags=["Авторизация"])


@auth_router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: AsyncSession = Depends(di.get_pg_session)):
    existing = await get_user_by_login(session, payload.login)
    if existing:
        raise HTTPException(status_code=409, detail="User with this login already exists")

    user = await create_user(session, payload.login, payload.password)

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)


@auth_router.post("/login", response_model=Token)
async def login(payload: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(di.get_pg_session)):
    user = await get_user_by_login(session, payload.username)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)
