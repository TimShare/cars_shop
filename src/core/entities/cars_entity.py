from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class Car:
    id: UUID = field(default_factory=uuid4)
    make: str  # Марка (e.g., "Toyota")
    model: str  # Модель (e.g., "Camry")
    year: int  # Год выпуска
    price: float  # Цена
    mileage: int  # Пробег (в километрах или милях)
    fuel_type: str  # Тип топлива (e.g., "Petrol", "Diesel", "Electric", "Hybrid")
    engine_capacity: float  # Объем двигателя (в литрах или куб. см)
    transmission: str  # Тип трансмиссии (e.g., "Automatic", "Manual")
    body_style: str  # Тип кузова (e.g., "Sedan", "SUV", "Hatchback", "Coupe", "Truck")
    color: str  # Цвет
    description: Optional[str] = None  # Описание (опционально)
    condition: str = "Used"  # Состояние ("New", "Used", "Certified Pre-Owned")
    vin: Optional[str] = None # VIN
    features: List[str] = field(default_factory=list)  # Список особенностей/опций (e.g., "ABS", "Airbags", "Navigation", "Sunroof")
    images: List["Image"] = field(default_factory=list)  # Список изображений (связь с другой сущностью)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Image:  # Отдельная сущность для изображений
    id: UUID = field(default_factory=uuid4)
    car_id: UUID  # Ссылка на Car, к которому относится изображение
    url: str  # URL изображения (или путь к файлу)
    description: Optional[str] = None  # Описание изображения (опционально)
    is_main: bool = False # главное ли фото
    created_at: datetime = field(default_factory=datetime.now)
    uploaded_at: datetime = field(default_factory=datetime.now)