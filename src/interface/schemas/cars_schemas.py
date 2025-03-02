from pydantic import BaseModel, HttpUrl, UUID4, validator
from typing import List, Optional
from datetime import datetime

class ImageBase(BaseModel):
    url: str  #  Может быть HttpUrl, если вы хотите валидировать URL
    description: Optional[str] = None
    is_main: bool = False

class ImageCreate(ImageBase):
    car_id: UUID4  #  Нужен при создании

class ImageUpdate(ImageBase):
    url: Optional[str] = None
    description: Optional[str] = None
    is_main: Optional[bool] = None

class ImageResponse(ImageBase):
    id: UUID4
    car_id: UUID4
    created_at: datetime
    uploaded_at: datetime

    class Config:
        orm_mode = True

class CarBase(BaseModel):
    make: str
    model: str
    year: int
    price: float
    mileage: int
    fuel_type: str
    engine_capacity: float
    transmission: str
    body_style: str
    color: str
    description: Optional[str] = None
    condition: str = "Used"
    vin: Optional[str] = None
    features: List[str] = []

class CarCreate(CarBase):
    pass # Features are optional

class CarUpdate(CarBase):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    mileage: Optional[int] = None
    fuel_type: Optional[str] = None
    engine_capacity: Optional[float] = None
    transmission: Optional[str] = None
    body_style: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    vin: Optional[str] = None
    features: Optional[List[str]] = None

class CarResponse(CarBase):
    id: UUID4
    images: List[ImageResponse] = [] # Include images in the response
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True