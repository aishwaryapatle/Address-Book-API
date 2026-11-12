from fastapi import APIRouter

from app.api.v1.addresses import router as addresses_router


api_router = APIRouter()
api_router.include_router(addresses_router)
