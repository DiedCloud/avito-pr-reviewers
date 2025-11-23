from enum import StrEnum

from pydantic import StrictStr

from src.controller.schemas.base import DatetimeBaseModel


class ErrorCode(StrEnum):
    TEAM_EXISTS = "TEAM_EXISTS"
    PR_EXISTS = "PR_EXISTS"
    PR_MERGED = "PR_MERGED"
    NOT_ASSIGNED = "NOT_ASSIGNED"
    NO_CANDIDATE = "NO_CANDIDATE"
    NOT_FOUND = "NOT_FOUND"


class Error(DatetimeBaseModel):
    code: ErrorCode
    message: StrictStr


class ErrorResponse(DatetimeBaseModel):
    error: Error
