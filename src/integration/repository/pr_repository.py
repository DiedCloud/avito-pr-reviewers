from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.integration.repository.entity import PRStatus, PullRequest, User, pr_reviewers
from src.service.generic.logger import logger


class PullRequestRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(di.get_pg_session)]):
        self.session = session

    async def create(self, pr_id: int, pr_name: str, author_id: int) -> PullRequest:
        pr = PullRequest(id=pr_id, name=pr_name, status=PRStatus.OPEN, author_id=author_id)
        self.session.add(pr)
        return pr

    async def get_by_id(self, pr_id: int) -> PullRequest | None:
        return await self.session.get(PullRequest, pr_id)

    async def get_reviews(self, user_id: int) -> Sequence[PullRequest]:
        q = (
            select(PullRequest)
            .join(PullRequest.assigned_reviewers)
            .where(User.id == user_id)
            .order_by(PullRequest.created_at.desc())
        )
        logger.debug(q)
        res = await self.session.execute(q)
        return res.scalars().all()

    async def change_reviewer(self, pr_id: int, new_user_id: int, old_user_id: int):
        q = text("""
                 UPDATE pr_reviewers
                 SET user_id = :new_user_id
                 WHERE pr_id = :pr_id
                   AND user_id = :old_user_id;
                 """)
        return await self.session.execute(q, {"pr_id": pr_id, "old_user_id": old_user_id, "new_user_id": new_user_id})

    async def add_reviewers(self, pr_id: int, users: Sequence[User]):
        values = [{"pr_id": pr_id, "user_id": u.id} for u in users]
        q = insert(pr_reviewers).values(values).on_conflict_do_nothing()
        return await self.session.execute(q)
