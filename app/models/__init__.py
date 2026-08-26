"""
Modelos SQLAlchemy del dominio.

Importarlos aqui es lo que hace que queden registrados en `Base.metadata`,
que es de donde Alembic lee el esquema para autogenerar las migraciones.
"""

from app.models.type import Type, TypeEffectiveness

__all__ = ["Type", "TypeEffectiveness"]
