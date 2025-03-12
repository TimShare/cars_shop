from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession  # AsyncEngine

from core.entities import Car as CarEntity
from core.entities import Image as ImageEntity
from infrastructure.models import CarModel
from core.repositories import ICarRepository, IImageRepository
from infrastructure.models.cars_models import (
    ImageModel,
)  # Corrected import path if needed


class CarRepository(ICarRepository):
    def __init__(self, session: AsyncSession):  # Принимаем AsyncSession
        self.session = session

    async def _to_entity(self, car_model: CarModel) -> CarEntity:
        """Преобразует объект SQLAlchemy CarModel в доменную сущность Car."""
        return CarEntity(
            id=car_model.id,
            make=car_model.make,
            model=car_model.model,
            year=car_model.year,
            price=car_model.price,
            mileage=car_model.mileage,
            fuel_type=car_model.fuel_type,
            engine_capacity=car_model.engine_capacity,
            transmission=car_model.transmission,
            body_style=car_model.body_style,
            color=car_model.color,
            description=car_model.description,
            condition=car_model.condition,
            vin=car_model.vin,
            features=car_model.features.split(",") if car_model.features else [],
            images=[],  # Изображения загружаются через ImageRepository
            created_at=car_model.created_at,
            updated_at=car_model.updated_at,
        )

    async def get(self, **filters) -> Optional[CarEntity]:
        stmt = (
            select(CarModel).filter_by(**filters).options(selectinload(CarModel.images))
        )
        result = await self.session.execute(stmt)
        car_model = result.scalars().first()
        if not car_model:
            return None
        return await self._to_entity(car_model)

    async def get_multi(self, offset: int, limit: int, **filters) -> List[CarEntity]:
        stmt = (
            select(CarModel)
            .filter_by(**filters)
            .offset(offset)
            .limit(limit)
            .options(selectinload(CarModel.images))
        )
        result = await self.session.execute(stmt)
        car_models = result.scalars().all()
        return [await self._to_entity(car_model) for car_model in car_models]

    async def create(self, data: CarEntity) -> CarEntity:
        if data is None:
            raise ValueError("Data cannot be None")

        car_model = CarModel(
            make=data.make,
            model=data.model,
            year=data.year,
            price=data.price,
            mileage=data.mileage,
            fuel_type=data.fuel_type,
            engine_capacity=data.engine_capacity,
            transmission=data.transmission,
            body_style=data.body_style,
            color=data.color,
            description=data.description,
            condition=data.condition,
            vin=data.vin,
            features=",".join(data.features) if data.features else None,
            # images = data.images  #  Убрано!  Изображения создаются через ImageRepository
        )
        self.session.add(car_model)
        await self.session.commit()
        await self.session.refresh(car_model)
        return await self._to_entity(car_model)

    async def update(self, car_id: UUID, data: CarEntity) -> Optional[CarEntity]:
        stmt = (
            update(CarModel)
            .values(
                make=data.make,
                model=data.model,
                year=data.year,
                price=data.price,
                mileage=data.mileage,
                fuel_type=data.fuel_type,
                engine_capacity=data.engine_capacity,
                transmission=data.transmission,
                body_style=data.body_style,
                color=data.color,
                description=data.description,
                condition=data.condition,
                vin=data.vin,
                features=",".join(data.features) if data.features else None,
                # images = data.images # Убрано!
            )
            .where(CarModel.id == car_id)
            .returning(CarModel)
        )
        result = await self.session.execute(stmt)
        car_model = result.scalars().first()
        if not car_model:
            return None
        await self.session.commit()  # Добавили commit
        return await self._to_entity(car_model)

    async def delete(self, car_id: UUID) -> None:
        stmt = delete(CarModel).where(CarModel.id == car_id)
        await self.session.execute(stmt)
        await self.session.commit()


class ImageRepository(IImageRepository):
    def __init__(self, session: AsyncSession):  # Принимаем AsyncSession
        self.session = session

    async def get_by_car_id(self, car_id: UUID) -> List[ImageEntity]:
        stmt = select(ImageModel).where(ImageModel.car_id == car_id)
        result = await self.session.execute(stmt)
        return [
            ImageEntity(
                id=image.id,
                car_id=image.car_id,
                url=image.url,
                description=image.description,
                is_main=image.is_main,
                created_at=image.created_at,
                uploaded_at=image.uploaded_at,
            )
            for image in result.scalars().all()
        ]

    async def create(self, image: ImageEntity) -> ImageEntity:

        if image is None:
            raise ValueError("Image cannot be None")

        image_model = ImageModel(**image.__dict__)
        self.session.add(image_model)
        await self.session.commit()
        await self.session.refresh(image_model)
        return ImageEntity(**image_model.__dict__)

    async def delete(self, image_id: UUID) -> None:
        stmt = delete(ImageModel).where(ImageModel.id == image_id)
        await self.session.execute(stmt)
        await self.session.commit()
