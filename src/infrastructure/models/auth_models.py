from datetime import datetime
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from infrastructure.models.base_model import BaseModelMixin
from infrastructure.postgres_db import Base


class BannedRefreshToken(Base, BaseModelMixin):
    __tablename__ = "BannedRefreshTokens"

    jti: Mapped[str] = mapped_column(nullable=False, unique=True)


class Profile(Base, BaseModelMixin):
    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True
    )
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    middle_name: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)

    user = relationship("User", back_populates="profile")


class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    blocked_at: Mapped[datetime] = mapped_column(nullable=True)

    profile = relationship(
        "Profile", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )
