from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from src.common.di_container import di
from src.controller.schemas.error_response import ErrorResponse
from src.controller.schemas.mapper import map_pr
from src.controller.schemas.pull_request import (
    PullRequestCreateResponse,
    PullRequestCreateRequest,
    PullRequestMergeRequest,
    PullRequestReassignResponse,
    PullRequestReassignRequest,
    str_to_int_pr_id,
)
from src.controller.schemas.user import str_to_int_user_id
from src.service.pr_service import create_pr, merge_pr, reassign_reviewers

pr_router = APIRouter(prefix="/pullRequest", tags=["PullRequests"])


@pr_router.post(
    "/create",
    responses={
        201: {"model": PullRequestCreateResponse, "description": "PR создан"},
        404: {"model": ErrorResponse, "description": "Автор/команда не найдены"},
        409: {"model": ErrorResponse, "description": "PR уже существует"},
    },
    summary="Создать PR и автоматически назначить до 2 ревьюверов из команды автора",
    response_model_by_alias=True,
)
async def pull_request_create(
    payload: PullRequestCreateRequest,
    session: AsyncSession = Depends(di.get_pg_session),
):
    pr_id = str_to_int_pr_id(payload.pull_request_id)
    author_id = str_to_int_user_id(payload.author_id)

    pr = await create_pr(pr_id, payload.pull_request_name, author_id, session)
    return JSONResponse(
        status_code=201,
        content=PullRequestCreateResponse(pr=map_pr(pr))
    )


@pr_router.post(
    "/merge",
    responses={
        200: {"model": PullRequestCreateResponse, "description": "PR в состоянии MERGED"},
        404: {"model": ErrorResponse, "description": "PR не найден"},
    },
    summary="Пометить PR как MERGED (идемпотентная операция)",
    response_model_by_alias=True,
)
async def pull_request_merge(
    payload: PullRequestMergeRequest,
    session: AsyncSession = Depends(di.get_pg_session),
) -> PullRequestCreateResponse:
    pr_id = str_to_int_pr_id(payload.pull_request_id)

    pr = await merge_pr(pr_id, session)
    return PullRequestCreateResponse(pr=map_pr(pr))


@pr_router.post(
    "/reassign",
    responses={
        200: {"model": PullRequestReassignResponse, "description": "Переназначение выполнено"},
        404: {"model": ErrorResponse, "description": "PR или пользователь не найден"},
        409: {"model": ErrorResponse, "description": "Нарушение доменных правил переназначения"},
    },
    summary="Переназначить конкретного ревьювера на другого из его команды",
    response_model_by_alias=True,
)
async def pull_request_reassign(
    payload: PullRequestReassignRequest,
    session: AsyncSession = Depends(di.get_pg_session),
) -> PullRequestReassignResponse:
    pr_id = str_to_int_pr_id(payload.pull_request_id)
    old_user_id = str_to_int_user_id(payload.old_user_id)

    pr, replaced_by = await reassign_reviewers(pr_id, old_user_id, session)
    return PullRequestReassignResponse(pr=map_pr(pr), replaced_by=replaced_by)
