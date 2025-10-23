"""
Alembic migration environment for FinInsight.
- Loads DATABASE_URL from .env using app.config.Settings (pydantic-settings)
- Imports all models in app/models/ for autogenerate
- Uses SQLAlchemy 2.0 style Base from app.database
"""
import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure app/ is on sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load settings from app.config (pydantic-settings loads .env)
from app.config import settings
from app.database import Base

# Dynamically import all models in app/models/
import importlib
import pkgutil
import app.models

def import_all_models():
    package = app.models
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        importlib.import_module(f"app.models.{module_name}")

import_all_models()

# Alembic Config object
config = context.config

# Set up loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Target metadata for autogenerate
# This is the MetaData object from SQLAlchemy models
# Used by Alembic to detect schema changes
# All models must be imported before this is set

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
