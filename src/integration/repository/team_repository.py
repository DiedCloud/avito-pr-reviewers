from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.integration.repository.entity import Team, User


class TeamRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(di.get_pg_session)]):
        self.session = session

    async def create(self, team_name: str) -> Team:
        team = Team(name=team_name)
        self.session.add(team)
        return team

    async def get_by_name(self, name: str) -> Team | None:
        return await self.session.get(Team, name)

    async def get_count(self):
        q = select(func.count()).select_from(Team)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_team_user_counts(self) -> dict[str, int]:
        stmt = select(Team.name, func.count(User.id).label("user_count")).outerjoin(Team.members).group_by(Team.name)
        result = await self.session.execute(stmt)
        return {team: count for team, count in result.all()}
