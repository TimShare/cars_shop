from core.repositories.cars_repository import ICarsRepository


class CarsService:

    def __init__(self, cars_repository: ICarsRepository):
        self.cars_repository = cars_repository

    def get_all_cars(self):
        return self.cars_repository.get_all_cars()

    def get_car_by_id(self, car_id):
        return self.cars_repository.get_car_by_id(car_id)

    def create_car(self, car_data):
        return self.cars_repository.create_car(car_data)

    def update_car(self, car_id, car_data):
        return self.cars_repository.update_car(car_id, car_data)

    def delete_car(self, car_id):
        return self.cars_repository.delete_car(car_id)
