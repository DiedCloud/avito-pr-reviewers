from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.controller.schemas.error_response import ErrorResponse
from src.controller.schemas.mapper import map_pr_short, map_user
from src.controller.schemas.user import (
    UsersGetReviewResponse,
    UsersSetIsActiveRequest,
    UsersSetIsActiveResponse,
    str_to_int_user_id,
)
from src.service.user_service import get_reviews, set_is_active


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "/getReview",
    responses={
        200: {"model": UsersGetReviewResponse, "description": "Список PR&#39;ов пользователя"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
    summary="Получить PR&#39;ы, где пользователь назначен ревьювером",
    response_model_by_alias=True,
)
async def user_get_review(
    user_id: str = Query(description="Идентификатор пользователя", alias="user_id"),
    session: AsyncSession = Depends(di.get_pg_session),
) -> UsersGetReviewResponse:
    validated_user_id = str_to_int_user_id(user_id)

    prs = await get_reviews(validated_user_id, session)

    return UsersGetReviewResponse(
        user_id=user_id,
        pull_requests=list(map(map_pr_short, prs)),
    )


@user_router.post(
    "/setIsActive",
    responses={
        200: {"model": UsersSetIsActiveResponse, "description": "Обновлённый пользователь"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
    summary="Установить флаг активности пользователя",
    response_model_by_alias=True,
)
async def user_set_is_active_post(
    payload: UsersSetIsActiveRequest,
    session: AsyncSession = Depends(di.get_pg_session),
) -> UsersSetIsActiveResponse:
    user_id = str_to_int_user_id(payload.user_id)

    user = await set_is_active(user_id, payload.is_active, session)

    return UsersSetIsActiveResponse(user=map_user(user))
