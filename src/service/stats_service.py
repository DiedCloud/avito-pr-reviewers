from sqlalchemy.ext.asyncio import AsyncSession

from src.controller.schemas.stats import StatsResponse
from src.integration.repository.pr_repository import PullRequestRepository
from src.integration.repository.team_repository import TeamRepository
from src.integration.repository.user_repository import UserRepository


async def get_get_stats(session: AsyncSession) -> StatsResponse:
    user_repo = UserRepository(session)
    pr_repo = PullRequestRepository(session)
    team_repo = TeamRepository(session)

    users_count_by_team = await team_repo.get_team_user_counts()
    avg_user_in_team = sum(users_count_by_team.values()) / len(users_count_by_team)

    prs_count_by_user = await pr_repo.get_prs_count_per_user()
    avg_prs_per_user = sum(prs_count_by_user.values()) / len(prs_count_by_user)

    return StatsResponse(
        users=await user_repo.get_count(),
        teams=await team_repo.get_count(),
        pull_requests=await pr_repo.get_count(),
        pr_assigns=await pr_repo.get_reviews_count(),
        avg_user_in_team=avg_user_in_team,
        users_count_by_team=users_count_by_team,
        avg_prs_per_user=avg_prs_per_user,
        prs_count_by_user={f"u{user}": count for user, count in prs_count_by_user.items()},
    )
