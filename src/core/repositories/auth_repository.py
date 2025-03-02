from typing import List
from abc import ABC, abstractmethod

from core.entities.auth_entity import BannedRefreshToken, User


class IUserRepository(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs) -> User | None:
        pass

    @abstractmethod
    async def get_multi(self, offset: int, limit: int, *args, **kwargs) -> List[User]:
        pass

    @abstractmethod
    async def create(self, data: User) -> User:
        pass

    @abstractmethod
    async def update(self, data: User, **filters) -> User:
        pass

    @abstractmethod
    async def delete(self, **filters) -> User:
        pass

class IBannedRefreshTokenRepository(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs) -> BannedRefreshToken | None:
        pass

    @abstractmethod
    async def create(self, data: BannedRefreshToken) -> BannedRefreshToken:
        pass

class IProfileRepository(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs) -> User | None:
        pass

    @abstractmethod
    async def update(self, data: User, **filters) -> User:
        pass
