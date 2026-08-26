import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"Iniciando servidor backend en http://{settings.HOST}:{settings.PORT}")
    print(f"Documentacion Swagger disponible en http://{settings.HOST}:{settings.PORT}/docs")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
