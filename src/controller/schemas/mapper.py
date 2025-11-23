from src.controller.schemas.pull_request import PullRequest as PullRequestDTO
from src.controller.schemas.pull_request import PullRequestShort
from src.controller.schemas.team import Team as TeamDTO
from src.controller.schemas.team import TeamMember
from src.controller.schemas.user import User as UserDTO
from src.integration.repository.entity import PullRequest, Team, User


def map_team(team: Team) -> TeamDTO:
    return TeamDTO(
        team_name=team.name,
        members=list(map(map_team_member, team.members)),
    )


def map_team_member(team_member: User | None) -> TeamMember | None:
    return (
        TeamMember(
            user_id=f"u{team_member.id}",
            username=team_member.username,
            is_active=team_member.is_active,
        )
        if team_member
        else None
    )


def map_user(user: User | None) -> UserDTO | None:
    return (
        UserDTO(
            user_id=f"u{user.id}",
            username=user.username,
            team_name=user.team_name,
            is_active=user.is_active,
        )
        if user
        else None
    )


def map_pr_short(pr: PullRequest) -> PullRequestShort | None:
    return (
        PullRequestShort(
            pull_request_id=f"pr-{pr.id}",
            pull_request_name=pr.name,
            author_id=pr.author_id,
            status=pr.status,
        )
        if pr
        else None
    )


def map_pr(pr: PullRequest) -> PullRequestDTO | None:
    return (
        PullRequestDTO(
            pull_request_id=f"pr-{pr.id}",
            pull_request_name=pr.name,
            author_id=f"u{pr.author_id}",
            status=pr.status,
            assigned_reviewers=list(map(lambda u: f"u{u.id}", pr.assigned_reviewers)),
            createdAt=pr.created_at,
            mergedAt=pr.merged_at,
        )
        if pr
        else None
    )
