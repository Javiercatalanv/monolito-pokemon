# Monolito Pokemon - Counter Team Builder (Backend)

Backend del sistema **Pokemon Counter Team Builder**, construido con
Arquitectura Monolitica Modular por Capas sobre FastAPI y expuesto como API REST
para el frontend en Angular, que vive en su propio repositorio.

El sistema permite configurar un equipo rival de 1 a 6 Pokemon (Gens 1 a 9) y
calcular automaticamente una escuadra counter optima evaluando ventajas de tipo
ofensivas (STAB), resistencias, inmunidades, estadisticas base y sinergia de equipo.

---

## Estructura del Proyecto

```text
monolito-pokemon/
│
├── app/
│   ├── api/                         # Controladores y Endpoints REST
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── pokemon.py       # Busqueda, catalogo y detalle de Pokemon
│   │       │   └── counter.py       # Generador de counters, analisis y presets
│   │       └── router.py            # Enrutador central API v1
│   ├── core/                        # Logica base, datos y configuracion
│   │   ├── config.py                # Variables de entorno y configuracion CORS
│   │   ├── database.py              # Configuracion de base de datos
│   │   ├── type_chart.py            # Matriz de efectividad de los 18 tipos elementales
│   │   └── pokemon_repository.py    # Repositorio de busqueda en memoria / JSON
│   ├── data/                        # Dataset de Pokedex nacional
│   │   └── pokedex.json
│   ├── schemas/                     # DTOs y validacion estricta (Pydantic v2)
│   │   ├── pokemon.py
│   │   └── counter.py
│   ├── services/                    # Capa de Logica de Negocio
│   │   └── counter_engine.py        # Algoritmo multi-estrategia de Counter Team
│   └── main.py                      # Instancia FastAPI, CORS y ciclo de vida
│
├── requirements.txt                 # Dependencias de Python
├── run.py                           # Script de inicio Uvicorn
├── .env                             # Variables de entorno
└── .env.example
```

---

## Puesta en Marcha

### Opcion 1: Script para Windows

Ejecutar `start-backend.bat`

---

### Opcion 2: Ejecucion Manual desde Terminal

```bash
# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias (si es necesario)
pip install -r requirements.txt

# Iniciar servidor
python run.py
```

* **API REST:** `http://127.0.0.1:8000`
* **Swagger UI (Documentacion interactiva):** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`

---

## Arquitectura y Patrones de Diseno

1. **Arquitectura por Capas:**
   - **Controladores (`app/api/v1/endpoints/`)**: Expone endpoints HTTP REST y gestiona codigos de estado.
   - **Capa de Logica de Negocio (`app/services/counter_engine.py`)**: Implementa el algoritmo de seleccion de counters, calculo de STAB y asignacion de roles.
   - **Capa de Acceso a Datos (`app/core/pokemon_repository.py`)**: Busqueda indexada en memoria para respuestas en milisegundos.
   - **Capa de Transferencia (`app/schemas/`)**: Tipado estricto con Pydantic v2.
2. **Inyeccion de Dependencias:**
   - Sistema `Depends` de FastAPI para sesiones de base de datos y servicios.
3. **CORS:**
   - Habilitado para permitir comunicacion entre `http://localhost:4200` y `http://127.0.0.1:8000`.

---

## Endpoints de la API REST

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/api/v1/pokemon` | Buscar y listar Pokemon con filtros por nombre y tipo |
| `GET` | `/api/v1/pokemon/types` | Listar los 18 tipos elementales y sus codigos de color |
| `GET` | `/api/v1/pokemon/{id_or_name}` | Obtener detalle de un Pokemon con matriz de debilidades |
| `GET` | `/api/v1/counter/presets` | Obtener equipos rivales preconfigurados de prueba |
| `POST` | `/api/v1/counter/analyze` | Analisis de debilidades y amenazas ofensivas del rival |
| `POST` | `/api/v1/counter/generate` | Generacion del Counter Team optimo segun estrategia |
