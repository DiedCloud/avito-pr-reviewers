from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.controller.schemas.error_response import ErrorResponse
from src.controller.schemas.mapper import map_team
from src.controller.schemas.team import Team, TeamAddResponse
from src.service.team_service import create_team, get_team_by_name


teams_router = APIRouter(prefix="/team", tags=["Teams"])


@teams_router.post(
    "/add",
    responses={
        201: {"model": TeamAddResponse, "description": "Команда создана"},
        400: {"model": ErrorResponse, "description": "Команда уже существует"},
    },
    summary="Создать команду с участниками (создаёт/обновляет пользователей)",
)
async def team_add_post(
    team: Team,
    session: AsyncSession = Depends(di.get_pg_session),
):
    team_entity = await create_team(team.team_name, team.members, session)
    return JSONResponse(status_code=201, content=TeamAddResponse(team=map_team(team_entity)))


@teams_router.get(
    "/get",
    responses={
        200: {"model": Team, "description": "Объект команды"},
        404: {"model": ErrorResponse, "description": "Команда не найдена"},
    },
    summary="Получить команду с участниками",
)
async def team_get(
    team_name: str = Query(None, description="Уникальное имя команды", alias="team_name"),
    session: AsyncSession = Depends(di.get_pg_session),
) -> Team:
    team_entity = await get_team_by_name(team_name, session)
    return map_team(team_entity)
