import re

from fastapi import HTTPException
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


def str_to_int_user_id(user_id: str) -> int:
    if not re.match("^u\d+$", user_id):
        raise HTTPException(status_code=422, detail="Неверный формат user_id")
    return int(user_id[1:])
