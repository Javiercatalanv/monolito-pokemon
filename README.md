# Monolito Pokemon - Counter Team Builder (Backend)

[![CI](https://github.com/Javiercatalanv/monolito-pokemon/actions/workflows/ci.yml/badge.svg)](https://github.com/Javiercatalanv/monolito-pokemon/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.14-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.19-6BA81E)

Backend del sistema **Pokemon Counter Team Builder**, construido con
Arquitectura Monolitica Modular por Capas sobre FastAPI y expuesto como API REST
para el frontend en Angular, que vive en su propio repositorio.

El sistema permite configurar un equipo rival de 1 a 6 Pokemon (Gens 1 a 9) y
calcular automaticamente una escuadra counter optima evaluando ventajas de tipo
ofensivas (STAB), resistencias, inmunidades, estadisticas base y sinergia de equipo.

El plan de trabajo completo, con la formalizacion del algoritmo de cobertura de
conjuntos y el cronograma de sprints, esta en [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## Estructura del Proyecto

```text
monolito-pokemon/
│
├── .github/workflows/
│   └── ci.yml                       # Lint, migraciones y tests contra PostgreSQL
│
├── app/
│   ├── api/                         # Controladores y Endpoints REST
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py        # Estado del sistema
│   │       │   ├── pokemon.py       # Busqueda, catalogo y detalle de Pokemon
│   │       │   └── counter.py       # Generador de counters, analisis y presets
│   │       └── router.py            # Enrutador central API v1
│   ├── core/                        # Logica base, datos y configuracion
│   │   ├── config.py                # Variables de entorno y configuracion CORS
│   │   ├── database.py              # Motor, sesion y Base declarativa
│   │   ├── type_chart.py            # Matriz 18x18 (seed y fallback offline)
│   │   └── pokemon_repository.py    # Repositorio en memoria / JSON (migra a SQL en S2)
│   ├── models/                      # Modelos SQLAlchemy 2.0 del dominio
│   │   ├── type.py                  # Type y TypeEffectiveness (matriz 18x18)
│   │   ├── pokemon.py               # Pokemon y PokemonType (N:M con slot)
│   │   └── team.py                  # Team, TeamMember y OptimizationRun
│   ├── repositories/                # Capa de Acceso a Datos
│   ├── data/                        # Dataset de Pokedex nacional
│   │   └── pokedex.json
│   ├── schemas/                     # DTOs y validacion estricta (Pydantic v2)
│   │   ├── health.py
│   │   ├── pokemon.py
│   │   └── counter.py
│   ├── services/                    # Capa de Logica de Negocio
│   │   └── counter_engine.py        # Algoritmo multi-estrategia de Counter Team
│   └── main.py                      # Instancia FastAPI, CORS y ciclo de vida
│
├── alembic/                         # Migraciones de base de datos
│   ├── versions/
│   └── env.py
│
├── tests/                           # Suite pytest
│   ├── conftest.py                  # Fixture de TestClient
│   └── api/
│
├── docs/
│   └── ROADMAP.md                   # Plan de accion, arquitectura y cronograma
│
├── docker-compose.yml               # PostgreSQL 16 para desarrollo local
├── alembic.ini
├── pyproject.toml                   # Configuracion de ruff, black, pytest y coverage
├── requirements.txt                 # Dependencias de runtime
├── requirements-dev.txt             # Dependencias de test y calidad
└── run.py                           # Script de inicio Uvicorn
```

---

## Puesta en Marcha

### Requisitos

| Herramienta | Version | Para que |
|---|---|---|
| Python | 3.14 | El motor de cobertura usa `int.bit_count()`, que requiere 3.10+ |
| Docker | cualquiera reciente | Levantar PostgreSQL 16 |

---

### 1. Base de datos

PostgreSQL corre en contenedor; es el unico componente que lo necesita.

```bash
docker compose up -d postgres
```

Queda escuchando en `localhost:5434`. Si ese puerto esta ocupado en tu maquina:

```bash
POSTGRES_PORT=5555 docker compose up -d postgres
```

y ajusta `DATABASE_URL` en `.env` para que apunte al mismo puerto.

---

### 2. Backend

```bash
# Entorno virtual
python3.14 -m venv venv
source venv/bin/activate          # macOS / Linux
.\venv\Scripts\activate           # Windows

# Dependencias (las de desarrollo incluyen a las de runtime)
pip install -r requirements.txt -r requirements-dev.txt

# Configuracion
cp .env.example .env

# Esquema de base de datos
alembic upgrade head

# Servidor
python run.py
```

* **API REST:** `http://127.0.0.1:8000`
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`
* **Health check:** `http://127.0.0.1:8000/api/v1/health`

En Windows tambien existe `start-backend.bat` para el arranque rapido, pero
asume que la base de datos y las migraciones ya estan listas.

---

### Desarrollo

Estos son exactamente los comandos que corre GitHub Actions en cada Pull
Request, asi que conviene pasarlos en local antes de pushear:

```bash
ruff check .            # linter
black --check .         # formato
pytest                  # tests
pytest --cov            # tests con reporte de cobertura

alembic check           # detecta modelos cambiados sin migracion
```

#### Migraciones

```bash
alembic revision --autogenerate -m "descripcion del cambio"
alembic upgrade head
alembic downgrade -1
```

El esquema **no** se crea al arrancar la aplicacion: lo gestiona Alembic. Si
la app levanta pero las consultas fallan, casi siempre falta `alembic upgrade head`.

---

## Arquitectura y Patrones de Diseno

1. **Arquitectura por Capas:**
   - **Controladores (`app/api/v1/endpoints/`)**: Expone endpoints HTTP REST y gestiona codigos de estado.
   - **Capa de Logica de Negocio (`app/services/`)**: Algoritmo de seleccion de counters, calculo de STAB y asignacion de roles.
   - **Capa de Acceso a Datos (`app/repositories/`, `app/models/`)**: Modelos SQLAlchemy 2.0 y consultas aisladas de la logica de negocio.
   - **Capa de Transferencia (`app/schemas/`)**: Tipado estricto con Pydantic v2.
2. **Inyeccion de Dependencias:**
   - Sistema `Depends` de FastAPI para sesiones de base de datos y servicios.
3. **Persistencia:**
   - PostgreSQL 16 via psycopg 3, con el esquema gobernado por migraciones Alembic.
4. **CORS:**
   - Habilitado para permitir comunicacion con el frontend Angular en `http://localhost:4200`.

---

## Endpoints de la API REST

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/api/v1/health` | Estado del sistema, nombre y version del proyecto |
| `GET` | `/api/v1/pokemon` | Buscar y listar Pokemon con filtros por nombre y tipo |
| `GET` | `/api/v1/pokemon/types` | Listar los 18 tipos elementales y sus codigos de color |
| `GET` | `/api/v1/pokemon/{id_or_name}` | Obtener detalle de un Pokemon con matriz de debilidades |
| `GET` | `/api/v1/counter/presets` | Obtener equipos rivales preconfigurados de prueba |
| `POST` | `/api/v1/counter/analyze` | Analisis de debilidades y amenazas ofensivas del rival |
| `POST` | `/api/v1/counter/generate` | Generacion del Counter Team optimo segun estrategia |
