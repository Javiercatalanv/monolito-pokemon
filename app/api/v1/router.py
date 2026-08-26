from fastapi import APIRouter

from app.api.v1.endpoints import counter, health, pokemon

api_router = APIRouter()

# Registro de rutas modulares
api_router.include_router(health.router, prefix="/health", tags=["Estado del Sistema"])
api_router.include_router(pokemon.router, prefix="/pokemon", tags=["Pokedex y Datos"])
api_router.include_router(
    counter.router, prefix="/counter", tags=["Generador de Counter Team"]
)
