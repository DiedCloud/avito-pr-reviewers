from pydantic import StrictBool, StrictStr

from src.controller.schemas.base import DatetimeBaseModel
from src.controller.schemas.pull_request import PullRequestShort


class User(DatetimeBaseModel):
    user_id: StrictStr
    username: StrictStr
    team_name: StrictStr
    is_active: StrictBool


class UsersGetReviewResponse(DatetimeBaseModel):
    user_id: StrictStr
    pull_requests: list[PullRequestShort]


class UsersSetIsActiveRequest(DatetimeBaseModel):
    user_id: StrictStr
    is_active: StrictBool


class UsersSetIsActiveResponse(DatetimeBaseModel):
    user: User | None = None
