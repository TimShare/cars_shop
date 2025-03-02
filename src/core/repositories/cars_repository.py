from abc import ABC, abstractmethod
from ..entities import Car, Image


class ICarsRepository(ABC):
    @abstractmethod
    def get(self, *args, **kwargs) -> Car | None:
        pass

    @abstractmethod
    def get_multi(self, offset: int, limit: int, *args, **kwargs) -> list[Car]:
        pass

    @abstractmethod
    def create(self, data: Car) -> Car:
        pass

    @abstractmethod
    def update(self, data: Car, **filters) -> Car:
        pass

    @abstractmethod
    def delete(self, **filters) -> Car:
        pass


class IImageRepository(ABC):
    @abstractmethod
    def get(self, *args, **kwargs) -> Image | None:
        pass

    @abstractmethod
    def get_multi(self, offset: int, limit: int, *args, **kwargs) -> list[Image]:
        pass

    @abstractmethod
    def create(self, data) -> Image:
        pass

    @abstractmethod
    def update(self, data: Image, **filters) -> Image:
        pass

    @abstractmethod
    def delete(self, **filters) -> Image:
        pass
