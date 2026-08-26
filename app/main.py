from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # El esquema lo gestiona Alembic (`alembic upgrade head`), no la app.
    # Crear tablas en el arranque escondia las migraciones faltantes hasta
    # que aparecia una diferencia en produccion.
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="""
    ## Arquitectura Monolitica - API REST Backend
    Este backend provee servicios REST construidos con FastAPI y SQLAlchemy
    para el frontend en Angular.
    
    ### Funcionalidades:
    * **Arquitectura por capas**: Repositorios, Servicios, Esquemas y Controladores (Endpoints).
    * **Documentación interactiva**: Swagger UI y ReDoc.
    * **Validación de datos**: Pydantic v2.
    * **CORS Habilitado**: Comunicación directa con Angular en localhost:4200.
    """,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Configuracion de CORS para comunicacion con Angular
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Montar rutas de API v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirigir la raiz hacia la documentacion interactiva de Swagger"""
    return RedirectResponse(url="/docs")
