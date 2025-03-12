from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities import User
from interface.dependencies import get_auth_service
from core.services.auth_service import AuthService
from interface.schemas import UserCreate, UserResponse, TokenResponse
from core.exceptions import (
    AlreadyExists,
    NotFoundError,
    InvalidCredentials,
    InvalidTokenError,
)
from settings import get_settings

config = get_settings()


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # for swagger


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_create: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    try:
        created_user = await auth_service.register(
            user_create.email, user_create.password
        )
        return created_user
    except AlreadyExists as e:
        raise HTTPException(status_code=400, detail=str("User already exists"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token", response_model=TokenResponse)  #  Используем /token
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Logs in a user and returns access and refresh tokens (ROPCG)."""
    try:
        token = await auth_service.login(
            form_data.username, form_data.password, form_data.scopes
        )
        print(token.access_token_expires)
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=True if not config.is_debug_mode else False,
            samesite="lax",
            expires=token.access_token_expires,
        )
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            secure=True if not config.is_debug_mode else False,
            samesite="lax",
            expires=token.refresh_token_expires,
        )

        return TokenResponse(
            token_type=token.token_type,
            scopes=token.scopes,
            access_token_expires=token.access_token_expires,
            refresh_token_expires=token.refresh_token_expires,
        )
    except (NotFoundError, InvalidCredentials) as e:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    token = request.cookies.get("refresh_token")  # get refresh token
    if token:
        await auth_service.logout(token)  # logout
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}
