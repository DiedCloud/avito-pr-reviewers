from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.integration.repository.entity import Client


class AuthRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(di.get_pg_session)]):
        self.session = session

    async def create_user(self, login: str, password_hash: str) -> Client:
        user = Client(login=login, password=password_hash)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> Client | None:
        q = select(Client).where(Client.id == user_id)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def get_user_by_login(self, login: str) -> Client | None:
        q = select(Client).where(Client.login == login)
        res = await self.session.execute(q)
        return res.scalars().first()
