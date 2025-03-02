from fastapi import APIRouter, Depends, HTTPException

from interface.schemas.cars_schemas import CarCreate

router = APIRouter(prefix="/cars", tags=["cars"])

@router.get("/create")
async def create_car(data: CarCreate, ):
    pass
    