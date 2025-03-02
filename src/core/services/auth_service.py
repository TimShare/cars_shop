from datetime import datetime, timedelta
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

settings = get_settings()


class AuthService:
    def __init__(
        self, user_repo: IUserRepository, token_repo: IBannedRefreshTokenRepository
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # remove, not needed

    async def login(self, email: str, password: str) -> User | None:
        """
        Login user.  This method is ONLY for /authorize and NOT for /token.
        """
        user = await self.user_repo.get(email=email)
        if not user:
            raise NotFoundError("User not found")
        if not self.verify_password(password, user.hashed_password):
            raise InvalidCredentials("Invalid credentials")
        return user

    async def exchange_code_for_token(
        self, code: str, client_id: str, redirect_uri: str, client_secret: str = None
    ) -> Token:
        """Exchanges an authorization code for an access token and refresh token."""

        # 1. Verify the code
        try:
            payload = jwt.decode(
                code, settings.secret_key, algorithms=[settings.algorithm]
            )
            code_type = payload.get("type")
            if code_type != "authorization_code":
                raise InvalidGrantError("Invalid code type")

            user_id: str = payload.get("sub")
            stored_client_id: str = payload.get("client_id")
            stored_redirect_uri: str = payload.get("redirect_uri")
            # You might also have a 'jti' to check for code replay

            if (
                not user_id
                or stored_client_id != client_id
                or stored_redirect_uri != redirect_uri
            ):
                raise InvalidGrantError("Invalid authorization code")

        except jwt.PyJWTError:
            raise InvalidGrantError("Invalid authorization code")

        # 2. Get the user
        user = await self.user_repo.get_by_id(UUID(user_id))  # Convert to UUID
        if user is None:
            raise InvalidGrantError(
                "User not found"
            )  # Should not be possible, but good to check.

        # 3.  (Optional, for confidential clients) Verify client_secret
        #     You would typically have a separate repository/service to manage clients.
        #     if client_secret:  # Simplified example
        #         if not self.verify_client_secret(client_id, client_secret):
        #             raise UnauthorizedClientError()

        # 4. Generate tokens
        scopes = payload.get("scopes", [])  # get scopes from auth code
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "scopes": scopes},
            expires_delta=access_token_expires,
        )
        refresh_token = self.create_refresh_token(
            data={"sub": str(user.id), "scopes": scopes},
            expires_delta=refresh_token_expires,
        )

        # 5. Return the tokens
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            access_token_expires=datetime.utcnow() + access_token_expires,
            refresh_token_expires=datetime.utcnow() + refresh_token_expires,
            scopes=scopes,
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.refresh_token_expire_days
            )
        to_encode.update({"exp": expire, "type": "refresh"})
        jti = str(uuid4())
        to_encode.update({"jti": jti})
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    def create_authorization_code(
        self, client_id: str, redirect_uri: str, user_id: UUID, scopes: List[str]
    ) -> str:
        """Creates an authorization code."""

        data = {
            "sub": str(user_id),
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scopes": scopes,
            "type": "authorization_code",
            # You might also add a 'jti' for the authorization code
        }
        # Authorization codes should have a short lifespan (e.g., 10 minutes)
        expires_delta = timedelta(minutes=10)
        return self.create_access_token(
            data, expires_delta
        )  # Re-use create_access_token for simplicity

    async def get_current_user(self, token: str) -> User | None:
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise InvalidCredentials()
            jti: str = payload.get("jti")

            if jti and await self.token_repo.is_banned(jti):
                raise InvalidTokenError("Token has been revoked")

            user = await self.user_repo.get_by_id(UUID(user_id))
            if user is None:
                raise NotFoundError()
            return user

        except jwt.PyJWTError:
            raise InvalidTokenError()

    async def logout(self, token: str):
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            jti: str = payload.get("jti")
            if jti:
                await self.token_repo.add(jti)
        except jwt.PyJWTError:
            raise InvalidTokenError()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self.user_repo.get_by_id(user_id)


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
