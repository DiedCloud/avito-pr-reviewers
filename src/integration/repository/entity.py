from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, Boolean, Column, Table, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.integration.repository.base import Base


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<Client(id={self.id} login={self.login!r})>"


pr_reviewers = Table(
    "pr_reviewers",
    Base.metadata,
    Column("pr_id", Integer, ForeignKey("pull_requests.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Team(Base):
    __tablename__ = "teams"
    name: Mapped[str] = mapped_column(String(255), primary_key=True)

    members: Mapped[list["User"]] = relationship(
        "User",
        back_populates="team",
        lazy="selectin",
        passive_deletes=True,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    team_name: Mapped[str] = mapped_column(ForeignKey("teams.name", ondelete="SET NULL"), nullable=True, index=True)
    team: Mapped["Team"] = relationship("Team", back_populates="members", lazy="joined")

    created_prs: Mapped[list["PullRequest"]] = relationship(
        "PullRequest",
        back_populates="author",
        lazy="selectin",
        passive_deletes=True,
    )
    reviewing_prs: Mapped[list["PullRequest"]] = relationship(
        "PullRequest",
        secondary=pr_reviewers,
        back_populates="assigned_reviewers",
        lazy="selectin",
        passive_deletes=True,
    )


class PRStatus(StrEnum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[PRStatus] = mapped_column(
        SAEnum(PRStatus, native_enum=True), nullable=False, server_default=PRStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    merged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    author: Mapped["User"] = relationship("User", back_populates="created_prs", lazy="joined")

    assigned_reviewers: Mapped[list["User"]] = relationship(
        "User", secondary=pr_reviewers, back_populates="reviewing_prs", lazy="selectin"
    )
