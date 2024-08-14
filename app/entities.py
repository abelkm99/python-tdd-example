from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any
import uuid

from sqlalchemy import Column, Integer, Table
from sqlalchemy.orm import composite, registry


mapper_registry = registry()


class Entity:
    id: int = field(init=False)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


@dataclass
class Point:
    x: int
    y: int


@dataclass(eq=False)
class Location(Entity):
    p1: Point
    p2: Point


location_table = Table(
    "location",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("x1", Integer, nullable=False),
    Column("y1", Integer, nullable=False),
    Column("x2", Integer, nullable=False),
    Column("y2", Integer, nullable=False),
)


mapper_registry.map_imperatively(
    Location,
    location_table,
    # it's like saying p1 is a Point object that composes  tables x1 and x2
    properties={
        "p1": composite(Point, location_table.c.x1, location_table.c.y1, init=False),
        "p2": composite(Point, location_table.c.x2, location_table.c.y2, init=False),
    },
)


@dataclass(kw_only=True)
class UserEntity:
    id: uuid.UUID = field(default=uuid.uuid4())
    name: str
