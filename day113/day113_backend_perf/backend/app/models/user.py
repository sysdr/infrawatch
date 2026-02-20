from sqlalchemy import String, DateTime, ForeignKey, Index, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid
class Team(Base):
    __tablename__ = "teams"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    users: Mapped[list["User"]] = relationship("User", back_populates="team", lazy="noload")
class Role(Base):
    __tablename__ = "roles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_team_id", "team_id"), Index("ix_users_email", "email"), Index("ix_users_active_team", "team_id", "is_active"))
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    team_id: Mapped[str | None] = mapped_column(String, ForeignKey("teams.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    team: Mapped["Team | None"] = relationship("Team", back_populates="users", lazy="noload")
