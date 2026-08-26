from fastapi import APIRouter
from app.api.v1.endpoints import pokemon, counter

api_router = APIRouter()

# Registro de rutas modulares
api_router.include_router(pokemon.router, prefix="/pokemon", tags=["Pokedex y Datos"])
api_router.include_router(counter.router, prefix="/counter", tags=["Generador de Counter Team"])
