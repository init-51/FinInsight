import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# --- FIX 1: Explicitly load .env file ---
# This makes sure DATABASE_URL is available
from dotenv import load_dotenv
load_dotenv()

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- FIX 2: More robust model discovery for autogenerate ---
# Add your model's MetaData object here
# for 'autogenerate' support
from app.database import Base # Import your Base from your app's database file

# Dynamically import all model files so Alembic sees them
import importlib
import pkgutil
import app.models

def import_all_models():
    """Dynamically imports all modules in the app.models package."""
    package = app.models
    # Adjust path if your models are directly under app.models
    package_path = package.__path__
    prefix = package.__name__ + "."
    for _, module_name, _ in pkgutil.iter_modules(package_path, prefix):
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            # Handle cases where __init__.py itself tries to import models
            pass

import_all_models()

target_metadata = Base.metadata

# --- FIX 3: Ensure the database URL is always set in the config ---
# Get the database URL from the environment and set it in the config
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL is not set in the environment.")
config.set_main_option('sqlalchemy.url', db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
