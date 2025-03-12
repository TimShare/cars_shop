from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request

from interface.schemas.cars_schemas import CarCreate
from interface.dependencies import get_car_service
from core.services.car_service import CarService

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("/create")
async def create_car(
    data: CarCreate,
    request: Request,
    car_service: CarService = Depends(get_car_service),
):
    """
    Create a new car.
    """
    try:
        car = await car_service.create_car(data)
        return {"car": car}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get")
async def get_car(
    car_id: UUID,
    request: Request,
    car_service: CarService = Depends(get_car_service),
):
    """
    Get a car by ID.
    """
    try:
        car = await car_service.get_car_by_id(car_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        return {"car": car}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
