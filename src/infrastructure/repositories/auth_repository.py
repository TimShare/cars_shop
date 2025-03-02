from typing import List
from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError, DuplicateEntryError
from core.repositories import IBannedRefreshTokenRepository
from core.entities.auth_entity import Profile
from core.entities.auth_entity import User as UserEntity
from core.repositories.auth_repository import IProfileRepository, IUserRepository
from core.entities import Token
from infrastructure.models import User as UserModel


class TokenRepository(IBannedRefreshTokenRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, **filters) -> Token | None:
        pass

    async def create(self, data: Token) -> Token:
        pass


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, **filters) -> UserEntity | None:
        stmt = select(UserModel).filter_by(**filters)
        user = await self.db.execute(stmt)
        user = user.scalars().first()
        if not user:
            return None
        return UserEntity(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            last_login=user.last_login,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            blocked_at=user.blocked_at,
        )

    async def get_multi(self, offset: int, limit: int, **filters) -> List[UserEntity]:
        pass

    async def create(self, data: UserEntity) -> UserEntity:
        try:
            user_model = UserModel(
                email=data.email,
                hashed_password=data.hashed_password,
                is_active=data.is_active,
                is_superuser=data.is_superuser,
                last_login=data.last_login,
                blocked_at=data.blocked_at,
            )

            self.db.add(user_model)
            await self.db.commit()
            await self.db.refresh(user_model)

            user_entity = UserEntity(
                id=user_model.id,
                email=user_model.email,
                hashed_password=user_model.hashed_password,
                last_login=user_model.last_login,
                is_active=user_model.is_active,
                is_superuser=user_model.is_superuser,
                created_at=user_model.created_at,
                updated_at=user_model.updated_at,
                blocked_at=user_model.blocked_at,
            )

            return user_entity
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateEntryError(
                f"Пользователь с email {data.email} уже существует"
            )

    async def update(self, data: UserEntity, **filters) -> UserEntity:
        pass

    async def delete(self, **filters) -> UserEntity:
        pass


class ProfileRepository(IProfileRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, **filters) -> Profile | None:
        pass

    async def update(self, data: Profile, **filters) -> Profile:
        pass
