import functools
import uuid
from datetime import timedelta, datetime
from typing import Any

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidSignatureError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from settings import get_settings
from infrastructure.postgres_db import Database
from infrastructure.models.banned_refresh_token import BannedRefreshToken
from infrastructure.models.user_models import User
from schemas.auth_schemas import TokensSchema

config = get_settings()


class BaseTokenHelpers:
    ACCESS = "access"
    REFRESH = "refresh"

    INVALID_ACCESS_TOKEN_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is invalid."
    )
    INVALID_REFRESH_TOKEN_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid."
    )
    EXPIRED_TOKEN_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token."
    )

    @classmethod
    async def validate_access_token(cls, access_token: str) -> Any:
        """
        Checks if the access token is valid
        Returns decoded payload access token if valid, else raises an exception
        """
        try:
            decoded_payload = jwt.decode(
                access_token, config.secret_key, algorithms=["HS256"]
            )
        except ExpiredSignatureError:
            raise cls.EXPIRED_TOKEN_EXCEPTION
        except InvalidSignatureError:
            raise cls.INVALID_ACCESS_TOKEN_EXCEPTION
        except Exception as err:
            raise cls.INVALID_ACCESS_TOKEN_EXCEPTION
        return dict(decoded_payload)

    @classmethod
    async def validate_refresh_token(
        cls,
        refresh_token: str,
        db: Database,
    ) -> dict | None:
        """
        Checks if the refresh token is valid
        Returns True if the refresh token is valid
        """
        try:
            decoded_payload = jwt.decode(
                refresh_token, config.secret_key, algorithms=["HS256"]
            )
        except ExpiredSignatureError:
            raise cls.EXPIRED_TOKEN_EXCEPTION
        except InvalidSignatureError:
            raise cls.INVALID_REFRESH_TOKEN_EXCEPTION
        refresh_jti = decoded_payload["jti"]
        exp = decoded_payload["exp"]
        _type = decoded_payload["type"]
        if _type != cls.REFRESH:
            return None
        async with db.get_db_session() as session:
            banned_token = await session.execute(
                select(BannedRefreshToken).where(BannedRefreshToken.jti == refresh_jti)
            )
        if banned_token.first() is not None:
            return None
        return dict(decoded_payload)

    @classmethod
    def check_access_token_status(cls):
        """Проверка токена на актуальность"""

        def func_decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                access_token = kwargs.get("access_token")
                print(access_token)
                await cls.validate_access_token(access_token)
                return await func(**kwargs)

            return wrapper

        return func_decorator


class TokenHelpers(BaseTokenHelpers):
    @classmethod
    def create_access_token(cls, user_id: str, is_superuser: bool) -> tuple[str, str]:
        """
        Creates a new access token
        """
        jti = str(uuid.uuid4())
        payload_access = {
            "user_id": str(user_id),
            "jti": jti,
            "is_superuser": is_superuser,
            "type": cls.ACCESS,
            "exp": datetime.utcnow() + timedelta(seconds=config.access_expire_time),
        }
        access_token = jwt.encode(payload_access, config.secret_key, algorithm="HS256")

        return access_token, jti

    @classmethod
    def create_refresh_token(cls, user_id: str) -> tuple[str, str]:
        """
        Creates a new refresh token
        """
        jti = str(uuid.uuid4())
        payload_access = {
            "user_id": str(user_id),
            "jti": jti,
            "type": cls.REFRESH,
            "exp": datetime.utcnow() + timedelta(seconds=config.refresh_expire_time),
        }
        refresh_token = jwt.encode(payload_access, config.secret_key, algorithm="HS256")

        return refresh_token, jti

    @classmethod
    async def ban_refresh_token(
        cls,
        refresh_jwt: str,
        db: Database,
    ):
        """
        Блокировка refresh токена
        """
        refresh_payload = await cls.validate_refresh_token(refresh_jwt, db)
        if refresh_payload is None:
            raise cls.INVALID_REFRESH_TOKEN_EXCEPTION
        async with db.get_db_session() as session:
            banned_token = BannedRefreshToken(jti=refresh_payload.get("jti"))
            session.add(banned_token)
            await session.commit()
            return banned_token

    @classmethod
    async def generate_token_pair(cls, user: User):
        access_token, access_token_jti = cls.create_access_token(
            user.id, user.is_superuser
        )
        refresh_token, refresh_token_jti = cls.create_refresh_token(user.id)
        return TokensSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=False)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme.",
                )
            payload = await self.verify_jwt(credentials.credentials)
            if not await self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token or expired token.",
                )
            request.state.payload = payload
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code.",
            )

    @classmethod
    async def verify_jwt(cls, token: str) -> bool:
        try:
            payload = await TokenHelpers.validate_access_token(token)
        except:
            payload = None
        return payload
