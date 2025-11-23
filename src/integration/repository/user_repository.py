from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.integration.repository.entity import User
from src.service.generic.logger import logger


class UserRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(di.get_pg_session)]):
        self.session = session

    async def create_many(self, users: list[User]):
        if not users:
            return None

        q = insert(User).values(
            [{"id": u.id, "team_name": u.team_name, "is_active": u.is_active, "username": u.username} for u in users]
        )
        q = q.on_conflict_do_update(
            index_elements=[User.id],
            set_={
                "team_name": q.excluded.team_name,
                "is_active": q.excluded.is_active,
                "username": q.excluded.username,
            },
        )
        return await self.session.execute(q)

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_rand_active_user_by_team_name(
        self, team_name: str, used_users_ids: set[int], count: int = 1
    ) -> Sequence[User]:
        q = (
            select(User)
            .where(User.team_name == team_name, ~User.id.in_(used_users_ids), User.is_active)
            .order_by(func.random())
            .limit(count)
        )
        logger.debug(q)
        res = await self.session.execute(q)
        return res.scalars().all()

    async def get_count(self):
        q = select(func.count()).select_from(User)
        result = await self.session.execute(q)
        return result.scalar_one()
