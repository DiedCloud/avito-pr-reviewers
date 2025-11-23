from pydantic import StrictStr, StrictBool

from src.controller.schemas.base import DatetimeBaseModel


class TeamMember(DatetimeBaseModel):
    user_id: StrictStr
    username: StrictStr
    is_active: StrictBool


class Team(DatetimeBaseModel):
    team_name: StrictStr
    members: list[TeamMember]


class TeamAddResponse(DatetimeBaseModel):
    team: Team | None = None
