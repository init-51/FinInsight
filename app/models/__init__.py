# Models package for FinInsight
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

__all__ = ["Base"]
