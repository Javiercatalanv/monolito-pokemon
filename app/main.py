from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Importa modelos para que SQLAlchemy los reconozca
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar tablas de base de datos en el arranque (para SQLite / desarrollo)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="""
    ## Arquitectura Monolitica - API REST Backend
    Este backend provee servicios REST construidos con FastAPI y SQLAlchemy para el frontend en Angular.
    
    ### Funcionalidades:
    * **Arquitectura por capas**: Repositorios, Servicios, Esquemas y Controladores (Endpoints).
    * **Documentación interactiva**: Swagger UI y ReDoc.
    * **Validación de datos**: Pydantic v2.
    * **CORS Habilitado**: Comunicación directa con Angular en localhost:4200.
    """,
    version="1.0.0",
    lifespan=lifespan
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
