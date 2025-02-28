from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
    async_scoped_session,
)
from sqlalchemy.orm import declarative_base

from settings import get_settings

config = get_settings()


from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_scoped_session,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Database:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)

        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    def get_scope_session(self):
        return async_scoped_session(
            session_factory=self.session_factory, scopefunc=current_task
        )

    async def get_db_session(self):
        from sqlalchemy import exc

        session: AsyncSession = self.session_factory()
        try:
            yield session
        except exc.SQLAlchemyError as error:
            await session.rollback()
            raise
        finally:
            await session.close()


# database = Database(config.database_url)
database: Database = Database(config.database_url)