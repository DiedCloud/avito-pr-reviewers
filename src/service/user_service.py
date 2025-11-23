from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.integration.repository.entity import PullRequest, User
from src.integration.repository.pr_repository import PullRequestRepository
from src.integration.repository.user_repository import UserRepository


async def get_reviews(user_id: int, session: AsyncSession) -> list[PullRequest]:
    user_repo = UserRepository(session)
    pr_repo = PullRequestRepository(session)

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return list(await pr_repo.get_reviews(user_id))


async def set_is_active(user_id: int, is_active: bool, session: AsyncSession) -> User:
    user_repo = UserRepository(session)

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_active = is_active

    await session.commit()
    await session.refresh(user)
    return user
