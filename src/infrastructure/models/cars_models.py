from datetime import datetime
from uuid import uuid4
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from infrastructure.models.base_model import BaseModelMixin

Base = declarative_base()


class CarModel(Base, BaseModelMixin):
    __tablename__ = "cars"

    make: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    fuel_type: Mapped[str] = mapped_column(String, nullable=False)
    engine_capacity: Mapped[float] = mapped_column(Float, nullable=False)
    transmission: Mapped[str] = mapped_column(String, nullable=False)
    body_style: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    condition: Mapped[str] = mapped_column(String, default="Used")
    vin: Mapped[str] = mapped_column(String, unique=True)
    features: Mapped[str] = mapped_column(String)

    images: Mapped[list["ImageModel"]] = relationship(
        "ImageModel", back_populates="car", cascade="all, delete-orphan"
    )


class ImageModel(Base, BaseModelMixin):
    __tablename__ = "images"

    car_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cars.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)

    car: Mapped["CarModel"] = relationship("CarModel", back_populates="images")
