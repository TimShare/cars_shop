from uuid import UUID
from core.repositories.cars_repository import ICarRepository
from core.entities import Car
from core.entities import Image


class CarService:

    def __init__(self, cars_repository: ICarRepository):
        self.cars_repository = cars_repository

    def get_all_cars(self) -> list[Car]:
        return self.cars_repository.get()

    def get_car_by_id(self, car_id: UUID) -> Car | None:
        return self.cars_repository.get(id=car_id)

    def create_car(self, car_data: Car) -> Car:
        return self.cars_repository.create(car_data)

    def update_car(self, car_id: UUID, car_data: Car) -> Car:
        return self.cars_repository.update(id=car_id, model=car_data)

    def delete_car(self, car_id: UUID) -> bool:
        return self.cars_repository.delete(id=car_id)
