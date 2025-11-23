from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.controller.schemas.team import TeamMember
from src.controller.schemas.user import str_to_int_user_id
from src.integration.repository.entity import Team, User
from src.integration.repository.team_repository import TeamRepository
from src.integration.repository.user_repository import UserRepository


async def create_team(team_name: str, team_members: list[TeamMember], session: AsyncSession) -> Team:
    team_repo = TeamRepository(session)
    user_repo = UserRepository(session)

    t = await team_repo.get_by_name(team_name)
    if t:
        raise HTTPException(status_code=400, detail="Команда уже существует")

    team_entity = await team_repo.create(team_name)

    users = [
        User(id=str_to_int_user_id(u.user_id), username=u.username, is_active=u.is_active, team_name=team_name)
        for u in team_members
    ]
    await user_repo.create_many(users)

    await session.commit()
    await session.refresh(team_entity)
    return team_entity


async def get_team_by_name(team_name: str, session: AsyncSession) -> Team:
    team_repo = TeamRepository(session)

    team = await team_repo.get_by_name(team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    return team
