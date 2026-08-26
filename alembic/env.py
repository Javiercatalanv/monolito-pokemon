"""Entorno de Alembic para el backend del Pokemon Counter Team Builder."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Importar el paquete de modelos es lo que puebla Base.metadata; sin esto
# el autogenerate produciria una migracion vacia.
import app.models  # noqa: F401
from app.core.config import settings
from app.core.database import Base

config = context.config

# Unica fuente de verdad para la conexion: la configuracion de la app.
# Se escapan los '%' porque configparser los interpreta como interpolacion.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse a la base (modo --sql)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones contra una conexion real."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Detectar cambios de tipo y de default evita migraciones que
            # "pasan" pero dejan el esquema distinto al de los modelos.
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
