from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request

from core.services.auth_service import AuthService
from interface.schemas.cars_schemas import CarCreate
from interface.dependencies import get_auth_service, get_car_service
from core.services.car_service import CarService

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("/create")
async def create_car(
    data: CarCreate,
    request: Request,
    car_service: CarService = Depends(get_car_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Create a new car.
    """
    access_token = request.cookies.get("access_token")
    if not access_token or not await auth_service.verify_access_token(access_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
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
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get a car by ID.
    """
    access_token = request.cookies.get("access_token")
    if not access_token or not await auth_service.verify_access_token(access_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        car = await car_service.get_car_by_id(car_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        return {"car": car}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
