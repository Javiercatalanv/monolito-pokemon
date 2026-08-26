# Plan de Acción — Pokémon Counter Team Builder

> **Entrega: jueves 1 de octubre de 2026.**
> Hoy es domingo 23 de agosto → quedan **38 días** (5 semanas de desarrollo + 4 días de cierre).
> **Congelamiento de código: domingo 27 de septiembre.** Del 28 de septiembre al 1 de octubre
> solo se toca documentación, informe y ensayo de la demo.
> Documento vivo: se actualiza al cerrar cada sprint.

---

## 1. Diagnóstico (23 de agosto de 2026)

Lo que **ya está** y funciona:

| Área | Estado |
|---|---|
| Backend FastAPI en capas (`api/` → `services/` → `core/`) | ✅ sólido |
| Matriz 18×18 de tipos (`core/type_chart.py`) | ✅ hardcodeada, correcta |
| Endpoints Pokédex + counter (`/pokemon`, `/counter`) | ✅ funcionando |
| Swagger / ReDoc autogenerado | ✅ base, sin pulir |
| Frontend Angular 22 standalone + servicios HTTP | ✅ funcionando |
| Dataset ~1025 Pokémon (`data/pokedex.json`) | ✅ 1 sola vez, script `build_dataset.py` |

Las **brechas reales** contra el objetivo declarado del proyecto:

| # | Brecha | Situación hoy | Riesgo |
|---|---|---|---|
| G1 | **No hay algoritmo de cobertura de conjuntos** | `counter_engine.py` es un scoring heurístico con pesos mágicos (`+70`, `-50`) y un filtro de diversidad de tipo primario | 🔴 Crítico — es *el* core |
| G2 | **No hay búsqueda local** | La selección es un `sort` + top-6 greedy sin refinamiento | 🔴 Crítico |
| G3 | **PostgreSQL no se usa** | `DATABASE_URL=sqlite:///./monolito.db`, y la única tabla es `items` (CRUD de ejemplo, ni registrado en `router.py`) | 🔴 Crítico |
| G4 | **No se consume PokeAPI** | El dataset viene de `Purukitto/pokemon-data.json` (GitHub raw); de PokeAPI solo se usan URLs de sprites | 🟠 Medio |
| G5 | **Cero tests** | Solo `app.spec.ts` autogenerado | 🔴 Crítico |
| G6 | **Cero CI/CD** | No existe `.github/` | 🔴 Crítico |
| G7 | Swagger sin pulir | Falta `response_model` en varios endpoints, sin ejemplos, sin esquemas de error | 🟠 Medio |
| G8 | Historial de git plano | 3 commits (`Initial commit`, `Update README`, `move directory`) | 🔴 Crítico |
| G9 | Solo se levanta en Windows | `.bat` sin equivalente `sh` ni Docker | 🟢 Bajo |

**Conclusión:** el proyecto está en ~40%. Lo que falta no es "más features": es el núcleo
algorítmico, la persistencia real y la evidencia de proceso. Con 38 días, el plan ataca
exactamente eso y **nada más**.

---

## 2. Alcance recortado (decisiones tomadas por la fecha)

Con 5 semanas no cabe todo. Esto se corta **a propósito**, y queda escrito para poder
defenderlo en la entrega en vez de que parezca olvido:

| Recortado | Por qué se puede |
|---|---|
| Publicar ReDoc en GitHub Pages | Swagger UI en `/docs` ya cumple el requisito de documentación |
| Dockerfiles de producción | `docker-compose` solo para PostgreSQL local/CI; el despliegue no es requisito |
| CodeQL / análisis de seguridad | No es requisito del proyecto |
| Sliders de pesos `α β γ δ` en la UI | Los pesos quedan como parámetros de la API y se calibran vía script |
| Gráfico de convergencia en el frontend | La traza se devuelve en el JSON y se muestra en el informe |
| Tabla `pokemon_moves` (STAB real por movimiento) | El STAB por tipo es una aproximación estándar y suficiente |
| Refactor del `counter-builder` en subcomponentes | Se extiende el componente existente; refactor cosmético no aporta nota |
| Meta de cobertura de tests 80% | Baja a **70%**, igual con gate en CI |

Lo que **no se negocia**, porque es lo que pide el enunciado: cobertura de conjuntos sobre
la matriz 18×18, búsqueda local, PokeAPI, PostgreSQL, API REST, Swagger y GitHub Actions.

---

## 3. Arquitectura objetivo

```
┌──────────────────────────── Angular 22 (SPA) ────────────────────────────┐
│  rival picker  │  coverage-matrix (heatmap 18×18)  │  resultado+métricas │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │ HTTP/JSON (documentado en OpenAPI 3.1)
┌────────────────────────────────▼─────────────────────────────────────────┐
│  FastAPI — monolito modular por capas                                    │
│                                                                          │
│  api/v1/endpoints/    pokemon · types · teams · runs · health             │
│         ↓                                                                │
│  services/            TeamOptimizer   ← greedy set cover + búsqueda local │
│                       CoverageEngine  ← bitmasks de 18 bits              │
│                       PokeApiSyncService                                 │
│         ↓                                                                │
│  repositories/        PokemonRepository · TypeRepository · RunRepository  │
│         ↓                                                                │
│  models/ (SQLAlchemy 2.0)  +  schemas/ (Pydantic v2)                     │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐        ┌──────────────────┐
                    │   PostgreSQL 16         │◀── ETL │     PokeAPI      │
                    │   (Alembic migrations)  │        │  /api/v2/...     │
                    └─────────────────────────┘        └──────────────────┘
```

### Esquema de base de datos (PostgreSQL)

```sql
types               (id, name, color)                              -- 18 filas
type_effectiveness  (attacking_type_id, defending_type_id, multiplier)  -- 324 filas = matriz 18×18
pokemon             (id, pokeapi_id, name, generation, is_legendary,
                     hp, attack, defense, sp_attack, sp_defense, speed, bst,
                     sprite_url, artwork_url, synced_at)
pokemon_types       (pokemon_id, type_id, slot)                    -- N:M
teams               (id, name, kind['rival'|'generated'], created_at)
team_members        (team_id, pokemon_id, slot)
optimization_runs   (id, rival_team_id, result_team_id, algorithm,
                     objective_value, coverage_pct, iterations, elapsed_ms,
                     params JSONB, created_at)
```

> `optimization_runs` es lo que hace que PostgreSQL **deje de ser decorativo**: cada
> ejecución del optimizador queda persistida y alimenta (a) el endpoint de historial,
> (b) la tabla de benchmarks del informe. La matriz 18×18 se mueve a `type_effectiveness`
> y `type_chart.py` pasa a ser *seed* y fallback para tests sin red.

---

## 4. El algoritmo (formalización)

Esto es lo que se defiende en la entrega, así que va escrito antes de codearlo.

### 4.1 Modelado como cobertura de conjuntos

Dado un equipo rival `R = {r₁..r₆}` y un pool de candidatos `P`, se busca `T ⊆ P`, `|T| = 6`.

**Cobertura defensiva** (esto es "minimizar debilidades"):
- Universo `U_def` = los 18 tipos atacantes.
- Peso de amenaza `w_t` = cuántos miembros de `R` tienen STAB de tipo `t`, ponderado por su
  mejor stat ofensivo. Los tipos que el rival no puede usar pesan un mínimo `ε` (no se
  ignoran: el equipo debe seguir siendo sano en general).
- El candidato `c` **cubre** `t` si `m(t → c) ≤ 0.5` (resiste o es inmune).
  `S_def(c) = { t ∈ U_def : m(t → c) ≤ 0.5 }`

**Cobertura ofensiva:**
- Universo `U_off = R`.
- `S_off(c) = { r ∈ R : máx_{ty ∈ types(c)} m(ty → r) ≥ 2 }`

Cubrir `U_def` con el mínimo de conjuntos es **minimum set cover** → NP-hard → se justifica
greedy (garantía `H₁₈ ≈ ln 18 ≈ 2.89` en el caso sin pesos) + refinamiento heurístico.

### 4.2 Función objetivo

```
J(T) =  α · Σ_{t∈U_def} w_t · 1[ ∃c∈T : t ∈ S_def(c) ]          ← cobertura defensiva
      − β · Σ_{t∈U_def} w_t · máx(0, n_weak(T,t) − 1)            ← penaliza debilidad COMPARTIDA
      + γ · |⋃_{c∈T} S_off(c)| / |U_off|                          ← cobertura ofensiva
      + δ · Σ_{c∈T} norm(BST_c)                                   ← desempate por poder base
```

`n_weak(T,t)` = miembros de `T` con `m(t → c) > 1`. **El término `β` es el corazón del
"minimizar debilidades"**: un equipo con 4 miembros débiles a Tierra es frágil aunque un
quinto la resista. Los pesos `α, β, γ, δ` son parámetros de la request y se calibran
empíricamente en S5 (queda documentado: no son números mágicos).

### 4.3 Fase 1 — Greedy

```
T ← ∅
mientras |T| < 6:
    c* ← argmax_{c ∈ P \ T} [ J(T ∪ {c}) − J(T) ]     # ganancia marginal
    T ← T ∪ {c*}
```

### 4.4 Fase 2 — Búsqueda local (1-swap, ascenso más pronunciado)

```
repetir:
    mejor_Δ ← 0
    para cada m ∈ T, para cada c ∈ P \ T:
        Δ ← J(T − {m} + {c}) − J(T)
        si Δ > mejor_Δ: guardar (m, c)
    si mejor_Δ ≤ 0: parar        # óptimo local
    aplicar el mejor swap
hasta max_iter
```

- Vecindad: `|T| × |P|` ≈ `6 × 600 ≈ 3600` evaluaciones por iteración.
- **Implementación con bitmasks:** `S_def(c)`, `S_weak(c)` y `S_off(c)` se precomputan como
  enteros de 18 bits; la cobertura del equipo es un `OR` y el conteo un `popcount`
  (`int.bit_count()`). Evaluar todo el vecindario baja a milisegundos.
- **Multi-start:** `k = 5` reinicios (greedy + 4 semillas aleatorias), se conserva el mejor
  `T`. Evita quedar atrapado en un óptimo local.
- Se registra la traza de `J` por iteración → gráfico de convergencia en el informe.

### 4.5 Benchmark (tabla obligatoria del informe)

| Algoritmo | `J` medio | Cobertura def. % | Debilidades compartidas | ms |
|---|---|---|---|---|
| `random` (baseline) | | | | |
| `heuristic_v1` (el actual) | | | | |
| `greedy` | | | | |
| `greedy + local_search` | | | | |
| `multistart + local_search` | | | | |

Los 5 quedan **seleccionables por API** (`?algorithm=`). Eso convierte el proyecto en algo
medible en vez de una caja negra, y es lo que sube la nota.

---

## 5. Reglas de trabajo (para que GitHub Actions demuestre el trabajo)

El historial *es* parte de la entrega. Con 38 días la meta realista es **~20 días distintos
con push y ~18 PRs**, no un commit gigante al final.

1. **CI en los primeros 2 días** (martes 25 como máximo). Todo push posterior queda con un
   check verde: eso es la evidencia.
2. **Una rama por tarea:** `feat/`, `fix/`, `test/`, `ci/`, `docs/`, `refactor/`, `perf/`.
   PR hacia `main`, esperar CI verde, mergear. Actions corre en el PR y en `main`.
3. **Merge commit o rebase-merge, nunca squash.** El squash borra los commits intermedios,
   que son justamente la prueba del proceso.
4. **Nunca `git push --force` sobre `main`.** Reescribir la historia destruye la evidencia.
5. **Conventional Commits** en imperativo y con alcance:
   `feat(optimizer): add greedy set cover over 18x18 matrix`
6. **Commits chicos:** 1 commit ≈ 1 idea, ≈ 50–250 líneas. 2–4 commits por sesión.
7. **Cadencia mínima: 4 días distintos por semana** con push (p. ej. mar/jue/sáb/dom).
8. **Tags por sprint:** `v0.1` … `v0.5`, `v1.0`.
9. Cada PR cierra un **issue**. Cargar los ~18 issues en un GitHub Project el día 1 toma
   20 minutos y se ve muy bien en la defensa.
10. **Repo público** (o con minutos de Actions disponibles) — si no, los workflows no corren.

### Workflows de GitHub Actions

| Archivo | Dispara en | Qué hace |
|---|---|---|
| `backend-ci.yml` | push/PR en `backend/**` | `ruff` + `black --check` + `pytest --cov` contra un **service container** de `postgres:16`; sube el reporte de cobertura como artifact |
| `frontend-ci.yml` | push/PR en `frontend/**` | `npm ci` + `ng build --configuration production` + `vitest run`; sube `dist/` como artifact |
| `openapi.yml` | push en `main` | Exporta `openapi.json` desde la app, lo valida con `openapi-spec-validator` y lo sube como artifact |

Badges de los 3 workflows al inicio del `README.md`.

---

## 6. Cronograma — 5 sprints + cierre

Cada sprint: **objetivo → ramas/commits → definición de terminado (DoD)**.

---

### S1 · lun 24 – dom 30 ago — CI + PostgreSQL + modelo de dominio
*Semana cargada a propósito: es infraestructura, no lógica, y todo lo demás depende de ella.
Los workflows salen primero para que el resto del sprint ya quede con checks verdes.*

| Rama | Commits |
|---|---|
| `docs/roadmap` | `docs: add action plan and architecture roadmap` |
| `ci/pipelines` | `chore(backend): add ruff, black and dev requirements` · `test(backend): add pytest setup with TestClient fixture` · `test(api): cover health and pokemon list endpoints` · `ci: add backend workflow with lint and pytest` · `ci: add frontend workflow with build and vitest` |
| `fix/router-registration` | `fix(api): register health router in api_router` |
| `feat/postgres-setup` | `feat(db): switch to psycopg driver and PostgreSQL URL` · `feat(infra): add docker-compose with postgres service` · `ci(backend): run tests against postgres service container` |
| `feat/domain-models` | `feat(models): add Type and TypeEffectiveness models` · `feat(models): add Pokemon and PokemonType models` · `feat(models): add Team, TeamMember and OptimizationRun models` |
| `feat/alembic` | `chore(db): initialize alembic` · `feat(db): add initial migration for domain schema` |
| `refactor/drop-items-demo` | `refactor: remove Item CRUD scaffolding` |
| `docs/badges` | `docs: add CI badges and setup instructions` |

**DoD:** 2 workflows verdes; `alembic upgrade head` crea las 7 tablas; los tests corren
contra Postgres real en CI; ≥6 tests pasando.
**Tag:** `v0.1`

---

### S2 · lun 31 ago – dom 6 sep — Ingesta desde PokeAPI
*El dato pasa a venir de la fuente que declara el proyecto, y los repositorios pasan a SQL.*

| Rama | Commits |
|---|---|
| `feat/pokeapi-client` | `feat(etl): add async PokeAPI client with httpx and rate limiting` · `feat(etl): cache raw responses to disk` · `test(etl): cover client with respx mocks` |
| `feat/type-matrix-sync` | `feat(etl): build 18x18 matrix from PokeAPI damage relations` · `test(etl): assert synced matrix matches reference type chart` |
| `feat/pokemon-sync` | `feat(etl): sync pokemon stats, types and species flags` · `feat(etl): add CLI entrypoint python -m app.etl.sync` |
| `feat/seed-fallback` | `feat(db): add offline seed from pokedex.json for CI` |
| `refactor/repository-to-sql` | `refactor(repositories): read pokemon from database instead of JSON` · `test(repositories): cover search and filter queries` |

**DoD:** `python -m app.etl.sync` puebla Postgres con ~1025 Pokémon + 324 filas de
efectividad; el test compara la matriz traída de la API contra `type_chart.py` (validación
cruzada — buen argumento para el informe); CI usa el seed offline, **sin red**; los
endpoints existentes siguen respondiendo igual.
**Tag:** `v0.2`

---

### S3 · lun 7 – dom 13 sep — Motor de cobertura + greedy set cover
*El sprint más importante. Cierra con una rebanada vertical funcionando de punta a punta.*

| Rama | Commits |
|---|---|
| `feat/coverage-engine` | `feat(coverage): add 18-bit bitmask representation of type coverage` · `test(coverage): verify resist, weak and immune masks per type combo` · `feat(coverage): add threat weighting from rival team STABs` |
| `feat/objective-function` | `feat(optimizer): add objective function with tunable weights` · `test(optimizer): assert shared weaknesses are penalized` |
| `feat/greedy-set-cover` | `feat(optimizer): add greedy set cover selection` · `test(optimizer): verify marginal gain ordering` · `test(optimizer): assert greedy covers all rival STAB types on known cases` |
| `feat/api-optimize` | `feat(schemas): add optimize request and response DTOs` · `feat(api): add POST /api/v1/teams/optimize with algorithm selector` · `test(api): cover optimize endpoint end to end` |

**DoD:** `POST /api/v1/teams/optimize` devuelve un equipo generado por greedy set cover, con
métricas de cobertura; tests sobre casos armados a mano (rival mono-tipo → el equipo debe
resistir ese tipo); cobertura de tests del módulo `optimizer` ≥85%.
**El endpoint viejo `/counter/generate` se mantiene vivo** (marcado `deprecated=True` en
Swagger) para que el frontend actual no se rompa.
**Tag:** `v0.3`

---

### S4 · lun 14 – dom 20 sep — Búsqueda local + persistencia + Swagger
| Rama | Commits |
|---|---|
| `feat/local-search` | `feat(optimizer): add 1-swap steepest ascent local search` · `feat(optimizer): record objective trace per iteration` · `test(optimizer): assert local search never worsens the objective` |
| `feat/multistart` | `feat(optimizer): add multi-start with seeded RNG` · `test(optimizer): assert deterministic results for a fixed seed` |
| `perf/optimizer` | `perf(optimizer): precompute candidate masks once per request` · `test(optimizer): assert optimization stays under 500ms for full pool` |
| `feat/baselines` | `feat(optimizer): add random and heuristic_v1 baselines for benchmarking` |
| `feat/api-runs` | `feat(api): persist optimization runs` · `feat(api): add GET /api/v1/runs history with pagination` |
| `feat/api-types` | `feat(api): expose GET /api/v1/types/matrix from database` |
| `docs/openapi` | `docs(api): add tags metadata, descriptions and error schemas` · `docs(api): add request/response examples to all endpoints` · `ci: validate openapi schema in CI` |

**DoD:** `local_search` mejora estrictamente el `J` de greedy en ≥80% de 100 equipos rivales
aleatorios (hay un test que lo verifica); resultados reproducibles con semilla fija; cada
llamada queda registrada en `optimization_runs`; `/docs` con todos los endpoints tipados,
con ejemplos y respuestas de error (`400`/`404`/`422`) documentadas.
**Tag:** `v0.4`

---

### S5 · lun 21 – dom 27 sep — Frontend, benchmark y endurecimiento
*Última semana de código. Cierre el domingo 27: **congelamiento**.*

| Rama | Commits |
|---|---|
| `feat/ui-optimize` | `feat(ui): point team builder to the new optimize endpoint` · `feat(ui): add algorithm selector` |
| `feat/ui-coverage-matrix` | `feat(ui): add 18x18 coverage heatmap component` · `feat(ui): highlight uncovered types and stacked weaknesses` · `test(ui): cover coverage matrix rendering` |
| `feat/ui-metrics` | `feat(ui): show objective value, coverage % and elapsed time` |
| `feat/benchmark` | `feat(bench): add benchmark script comparing all algorithms` · `docs: add benchmark results table` |
| `feat/observability` | `feat(core): add request timing middleware and structured logging` · `feat(api): add typed exception handlers` |
| `test/integration` | `test(integration): add end-to-end optimize flow against postgres` · `test(api): cover validation errors and edge cases` |
| `ci/coverage-gate` | `ci: fail the build under 70% backend coverage` |

**DoD:** el heatmap 18×18 muestra en rojo las debilidades sin cubrir del equipo generado;
cobertura backend ≥70% con gate en CI; tabla de benchmark llena con datos reales; los 3
workflows verdes; `docker compose up` + `alembic upgrade head` + `python -m app.etl.sync`
levanta el sistema desde cero.
**Tag:** `v1.0` 🎯

---

### Cierre · lun 28 sep – jue 1 oct — Documentación y demo
*Sin features nuevas. Solo `docs(...)` y `fix(...)` de lo que aparezca al escribir.*

| Día | Trabajo |
|---|---|
| **lun 28** | `docs: rewrite README with real setup, endpoints and screenshots` — el README actual describe cosas que no existen |
| **mar 29** | `docs: add layered architecture diagram and decision records (ADRs)` · `docs: document the set cover formulation and complexity` |
| **mié 30** | `docs: add final report with benchmark analysis` · ensayo completo de la demo de punta a punta |
| **jue 1 oct** | Entrega. Solo `fix` triviales si algo falla en el ensayo final. |

---

## 7. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| **S1 está sobrecargado** y arrastra atraso a todo el resto | Los workflows salen el día 1–2 en su versión mínima (lint + pytest, sin Postgres); el service container se agrega recién cuando Postgres aterriza a mitad de semana |
| El rate limit / caída de PokeAPI rompe el ETL o el CI | Caché en disco + seed offline desde `pokedex.json`; el CI **nunca** sale a la red |
| S3–S4 (el algoritmo) se atrasan | Son los sprints intocables. Lo que se sacrifica si hay atraso, en este orden: historial de runs (S4), observabilidad (S5), selector de algoritmo en la UI (S5), benchmark reducido a 3 algoritmos en vez de 5 |
| La calibración de `α β γ δ` se vuelve un pozo sin fondo | Valores por defecto fijos en S3; calibrar **solo** en S5 con el script de benchmark, con un límite duro de 4 horas |
| Angular 22 + `vitest` con poca documentación | Los tests de frontend se mantienen mínimos (1 servicio + 1 componente); el peso de los tests va al backend, donde está la lógica |
| Migrar a Postgres rompe lo que hoy funciona | S1 va **antes** del algoritmo y con CI ya en verde: cualquier regresión salta de inmediato |
| No queda tiempo para el informe | El cierre (28 sep – 1 oct) es intocable. Si S5 se atrasa, se recorta S5 — **no** el informe |

---

## 8. Checklist de entrega

- [ ] Algoritmo de cobertura de conjuntos sobre la matriz 18×18 — implementado y testeado
- [ ] Búsqueda local (1-swap + multi-start) con métricas de convergencia
- [ ] PostgreSQL con migraciones Alembic y dominio real persistido
- [ ] Ingesta desde PokeAPI con caché y fallback offline
- [ ] API REST versionada y documentada al 100% en Swagger/OpenAPI 3.1
- [ ] Frontend Angular con heatmap de cobertura 18×18 y métricas del algoritmo
- [ ] Cobertura de tests backend ≥70%, con gate en CI
- [ ] 3 workflows de GitHub Actions en verde
- [ ] Historial de git con pushes distribuidos en ~20 días y tags `v0.1`–`v1.0`
- [ ] Informe con tabla de benchmark y ADRs
