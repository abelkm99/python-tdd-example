from dataclasses import dataclass, field
from typing import Any
import uuid

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import composite, properties, registry, relationship


MapperRegistry = registry()


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
    MapperRegistry.metadata,
    Column("id", Integer, primary_key=True),
    Column("x1", Integer, nullable=False),
    Column("y1", Integer, nullable=False),
    Column("x2", Integer, nullable=False),
    Column("y2", Integer, nullable=False),
)


MapperRegistry.map_imperatively(
    Location,
    location_table,
    # it's like saying p1 is a Point object that composes  tables x1 and x2
    properties={
        "p1": composite(Point, location_table.c.x1, location_table.c.y1, init=False),
        "p2": composite(Point, location_table.c.x2, location_table.c.y2, init=False),
    },
)


# ------------ Domain Models -----------

"""
One-to-One Relationship
------------------------
Tables: User and Profile
Relationships: Each User has one Profile, and each Profile is associated with one User.
What to Show:
    How to create the one-to-one relationship.
    How to access the related Profile from a User instance and vice versa.
    How to handle cascading deletes.
"""


@dataclass(kw_only=True)
class UserEntity:
    id: uuid.UUID = field(default=uuid.uuid4())
    name: str

    profile: "ProfileEntitiy | None" = field(default=None, repr=False)


@dataclass(kw_only=True)
class ProfileEntitiy:
    id: uuid.UUID = field(default=uuid.uuid4())
    profile_picture: str
    user_id: uuid.UUID | None = field(default=None)
    # making this default=False will override the preovuis user id so becarefull with that too
    user: "UserEntity | None" = field(init=False, repr=False)


# --------------- ORM MAPPING ----------------


UserTable = Table(
    "user",
    MapperRegistry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    ),
    Column("name", String, nullable=False),
)


ProfileTable = Table(
    "profile",
    MapperRegistry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    ),
    Column("picture", String, nullable=False),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,  # let's make is optional if we can map optional fields the rest is easy
        unique=True,
    ),
)


# ------------ Mappings ------------

MapperRegistry.map_imperatively(
    UserEntity,
    UserTable,
    properties={
        "id": UserTable.c.id,
        "name": UserTable.c.name,
        "profile": relationship(ProfileEntitiy, uselist=False, back_populates="user"),
    },
)

MapperRegistry.map_imperatively(
    ProfileEntitiy,
    ProfileTable,
    properties={
        "id": ProfileTable.c.id,
        "profile_picture": ProfileTable.c.picture,  # I can map different attributes names with different column names
        "user": relationship(UserEntity, back_populates="profile"),
    },
)

"""
as a rule of thumb use the keys to create the relationship
for the relationship objects don't make the default none.
making this none would make the foriegn key is going to be None.
so when you insert a statement it's going to pass None.

this is not going to be an issue if the fields are optional
"""
