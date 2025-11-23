from datetime import datetime
from enum import StrEnum
from typing import List

from pydantic import StrictStr, Field

from src.controller.schemas.base import DatetimeBaseModel


class PRStatus(StrEnum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequest(DatetimeBaseModel):
    pull_request_id: StrictStr
    pull_request_name: StrictStr
    author_id: StrictStr
    status: PRStatus
    assigned_reviewers: List[StrictStr] = Field(description="user_id назначенных ревьюверов (0..2)", max_length=2)
    created_at: datetime | None = Field(default=None, alias="createdAt")
    merged_at: datetime | None = Field(default=None, alias="mergedAt")


class PullRequestShort(DatetimeBaseModel):
    pull_request_id: StrictStr
    pull_request_name: StrictStr
    author_id: StrictStr
    status: PRStatus


class PullRequestCreateRequest(DatetimeBaseModel):
    pull_request_id: StrictStr
    pull_request_name: StrictStr
    author_id: StrictStr


class PullRequestCreateResponse(DatetimeBaseModel):
    pr: PullRequest | None = None


class PullRequestMergeRequest(DatetimeBaseModel):
    pull_request_id: StrictStr


class PullRequestReassignRequest(DatetimeBaseModel):
    pull_request_id: StrictStr
    old_user_id: StrictStr


class PullRequestReassignResponse(DatetimeBaseModel):
    pr: PullRequest
    replaced_by: StrictStr = Field(description="user_id нового ревьювера")
