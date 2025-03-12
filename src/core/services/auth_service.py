from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID, uuid4

import jwt

from core.repositories import IUserRepository, IBannedRefreshTokenRepository
from core.entities.auth_entity import BannedRefreshToken, Token, User
from core.exceptions import (
    AlreadyExists,
    InvalidGrantError,
    InvalidTokenError,
    NotFoundError,
    InvalidCredentials,
)
from passlib.context import CryptContext

from settings import get_settings

config = get_settings()


class AuthService:
    def __init__(
        self, user_repo: IUserRepository, token_repo: IBannedRefreshTokenRepository
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register(self, email: str, password: str) -> User:
        existing_user = await self.user_repo.get(email=email)  # Исправлено
        if existing_user:
            raise AlreadyExists()  # Исправлено
        hashed_password = self.pwd_context.hash(password)
        new_user = User(email=email, hashed_password=hashed_password)
        created_user = await self.user_repo.create(new_user)
        return created_user

    async def login(self, email: str, password: str, scopes: List[str] = None) -> Token:
        user = await self.user_repo.get(email=email)  # Исправлено
        if not user:
            raise NotFoundError(
                "Incorrect email or password"
            )  # Более информативное сообщение
        if not self.verify_password(password, user.hashed_password):
            raise InvalidCredentials("Incorrect email or password")

        access_token_expires = timedelta(
            minutes=config.access_token_expire_minutes
        )  # Исправлено
        refresh_token_expires = timedelta(
            days=config.refresh_token_expire_days
        )  # Исправлено
        access_token = self.create_access_token(
            data={"sub": str(user.id), "scopes": scopes or []},  # Use user.id
            expires_delta=access_token_expires,
        )
        refresh_token = self.create_refresh_token(
            data={"sub": str(user.id), "scopes": scopes or []},  # Use user.id
            expires_delta=refresh_token_expires,
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            access_token_expires=datetime.now(timezone.utc) + access_token_expires,
            refresh_token_expires=datetime.now(timezone.utc) + refresh_token_expires,
            scopes=scopes or [],
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=config.access_token_expire_minutes
            )  # Исправлено
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, config.secret_key, algorithm=config.algorithm
        )
        return encoded_jwt

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=config.refresh_token_expire_days
            )  # Исправлено
        to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid4())})
        encoded_jwt = jwt.encode(
            to_encode, config.secret_key, algorithm=config.algorithm
        )
        return encoded_jwt

    async def verify_access_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(
                token, config.secret_key, algorithms=[config.algorithm]
            )
            if payload.get("type") != "access":  # Важно проверять тип токена
                return None
            user_id: str = payload.get("sub")  #  Извлекаем user_id (sub)
            if user_id is None:
                return None
            jti: str = payload.get(
                "jti"
            )  #  Извлекаем jti (не используется для access token)

            #  Проверяем, не находится ли JTI в черном списке (для refresh token)
            if jti and await self.token_repo.is_banned(jti):  # Исправлено
                return None

            user = await self.user_repo.get(
                id=UUID(user_id)
            )  #  Исправлено: get_by_id и UUID
            return user
        except jwt.PyJWTError:  #  Исправлено: ловим JWTError
            return None

    async def logout(self, token: str):
        """Invalidates the refresh token (adds its JTI to the banned tokens list)."""
        try:
            payload = jwt.decode(
                token, config.secret_key, algorithms=[config.algorithm]
            )
            jti: str = payload.get("jti")
            if jti:
                await self.token_repo.create(jti)  # Исправлено
        except jwt.PyJWTError:  # Исправлено
            raise InvalidTokenError()


class BannedTokensService:
    def __init__(self, repo: IBannedRefreshTokenRepository):
        self.repo = repo

    async def get(self, id: UUID) -> BannedRefreshToken | None:
        return await self.repo.get(id=id)

    async def create(self, data: BannedRefreshToken) -> BannedRefreshToken:
        token = await self.repo.get(email=data.email)
        if token:
            raise AlreadyExists("User already exists")
        return await self.repo.create(data)


class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def get(self, id: UUID) -> User | None:
        return await self.repo.get(id=id)
