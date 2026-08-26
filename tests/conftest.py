"""Fixtures compartidas por toda la suite de tests del backend."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """
    Cliente HTTP contra la aplicacion real.

    Se usa como context manager para que FastAPI ejecute el ciclo de vida
    (`lifespan`) igual que en produccion. El alcance es de sesion porque la
    app no guarda estado entre requests y levantarla una sola vez mantiene
    la suite rapida.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def api_prefix() -> str:
    """Prefijo de la API versionada, para no repetir el literal en cada test."""
    from app.core.config import settings

    return settings.API_V1_STR
