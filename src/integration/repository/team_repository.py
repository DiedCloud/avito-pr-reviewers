from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.integration.repository.entity import Team


class TeamRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(di.get_pg_session)]):
        self.session = session

    async def create(self, team_name: str) -> Team:
        team = Team(name=team_name)
        self.session.add(team)
        return team

    async def get_by_name(self, name: str) -> Team | None:
        return await self.session.get(Team, name)
