import logging
from typing import AsyncGenerator, Generator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.services import UserService
from core.services.auth_service import AuthService
from infrastructure.postgres_db import database
from infrastructure.repositories import UserRepository
from infrastructure.repositories import TokenRepository


async def get_user_service(
    session: AsyncSession = Depends(database.get_db_session),
):
    logging.warning(session)
    user_repository = UserRepository(session)
    service = UserService(user_repository)
    yield service


async def get_auth_service(
    session: AsyncSession = Depends(database.get_db_session),
):
    user_repository = UserRepository(session)
    token_repository = TokenRepository(session)
    service = AuthService(user_repository, token_repository)
    yield service
