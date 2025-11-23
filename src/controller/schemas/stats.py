from src.controller.schemas.base import DatetimeBaseModel


class StatsResponse(DatetimeBaseModel):
    users: int
    teams: int
    pull_requests: int
    pr_assigns: int
    avg_user_in_team: float
    users_count_by_team: dict[str, int]
    avg_prs_per_user: float
    prs_count_by_user: dict[str, int]
