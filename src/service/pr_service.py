from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.integration.repository.entity import PRStatus, PullRequest
from src.integration.repository.pr_repository import PullRequestRepository
from src.integration.repository.user_repository import UserRepository


async def create_pr(pr_id: int, pr_name: str, author_id: int, session: AsyncSession) -> PullRequest:
    pr_repo = PullRequestRepository(session)
    user_repo = UserRepository(session)

    pr = await pr_repo.get_by_id(pr_id)
    if pr:
        raise HTTPException(status_code=409, detail="PR уже существует")

    author = await user_repo.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Автор/команда не найдены")

    pr = await pr_repo.create(pr_id, pr_name, author_id)

    reviewers = await user_repo.get_rand_active_user_by_team_name(author.team_name, {author_id}, 2)
    await pr_repo.add_reviewers(pr_id, reviewers)

    await session.commit()
    await session.refresh(pr)
    return pr


async def merge_pr(pr_id: int, session: AsyncSession) -> PullRequest:
    repo = PullRequestRepository(session)

    pr = await repo.get_by_id(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR не найден")

    if pr.status != PRStatus.MERGED:
        pr.merged_at = datetime.now(UTC)
        pr.status = PRStatus.MERGED

        await session.commit()
        await session.refresh(pr)

    return pr


async def reassign_reviewers(pr_id: int, old_user_id: int, session: AsyncSession) -> tuple[PullRequest, int]:
    pr_repo = PullRequestRepository(session)
    user_repo = UserRepository(session)

    pr = await pr_repo.get_by_id(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR не найден")
    if pr.status == PRStatus.MERGED:
        raise HTTPException(status_code=409, detail="Нарушение доменных правил переназначения: PR уже MERGED")

    old_user = await user_repo.get_by_id(old_user_id)
    if not old_user:
        raise HTTPException(status_code=404, detail="Пользователь не найдены")
    replaced_by = old_user_id

    used_users = {u.id for u in pr.assigned_reviewers}
    if old_user_id not in used_users:
        raise HTTPException(
            status_code=409,
            detail=f"Нарушение доменных правил переназначения: Пользователь u{old_user_id} не был назначен на PR",
        )

    available_users = await user_repo.get_rand_active_user_by_team_name(old_user.team_name, used_users)
    if available_users:
        replaced_by = available_users[0].id
        await pr_repo.change_reviewer(pr_id, replaced_by, old_user_id)
        await session.commit()

    await session.refresh(pr)
    return pr, replaced_by
