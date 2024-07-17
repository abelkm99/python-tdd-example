from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import INTEGER, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import composite, registry, relationship

from enum import Enum

database_url = "postgresql+asyncpg://root:123456789@localhost:5432/example"
async_engine = create_async_engine(
    url=database_url,
    future=True,
    pool_size=20,
    max_overflow=20,
)


async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


mapper_registry = registry()


class Entity:
    id: int = field(init=False)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


class AggregateRoot(Entity):
    """
    An entry point of aggregate.
    """

    pass


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


@dataclass(eq=False)
class RoomStatus(Enum):
    PENDING = "pending"
    BOOKED = "booked"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CMP = "comp"

    def __composite_values__(self):
        return (self.value,)

    @classmethod
    def from_value(cls, value: Any) -> "RoomStatus":
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"{value} is not a valid value for RoomStatus")


@dataclass
class Room(Entity):
    name: str
    room_status: RoomStatus
    reservations: list["Reservation"] = field(default_factory=list)


@dataclass
class Reservation(Entity):
    room: Room
    date_in: datetime
    date_out: datetime


room_table = Table(
    "hotel_room",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(20), nullable=False, unique=True),
    Column("status", String(20), nullable=True),
)


reservation_table = Table(
    "room_reservation",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("room_id", Integer, ForeignKey("hotel_room.id"), nullable=False),
    Column("date_in", DateTime(timezone=True)),
    Column("date_out", DateTime(timezone=True)),
)

mapper_registry.map_imperatively(
    Room,
    room_table,
    properties={
        "room_status": composite(RoomStatus.from_value, room_table.c.status),
        "reservations": relationship(
            Reservation,
            back_populates="room",
            lazy="joined",
        ),
    },
)

mapper_registry.map_imperatively(
    Reservation,
    reservation_table,
    properties={
        "room": relationship(
            Room,
            back_populates="reservations",
            lazy="joined",
        ),
        # "room": relationship(
        #     Room,
        #     backref="reservations",
        #     lazy="joined",
        # ),
    },
)


@dataclass
class User:
    user_id: int
    name: str

    posts: list["Post"] = field(default_factory=list, repr=False)


@dataclass
class Post:
    post_id: int
    title: str
    user_id: int = field(init=False)

    user: User = field(init=False, repr=False)


user_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", INTEGER, primary_key=True, autoincrement=True),
    Column("name", String(500)),
)

posts_table = Table(
    "post",
    mapper_registry.metadata,
    Column("id", INTEGER, primary_key=True, autoincrement=True),
    Column("title", String(500)),
    Column("user_id", INTEGER, ForeignKey("users.id"), nullable=False),
)

mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "user_id": user_table.c.id,
        "posts": relationship(
            Post,
            back_populates="user",
        ),
    },
)

mapper_registry.map_imperatively(
    Post,
    posts_table,
    properties={
        "post_id": posts_table.c.id,
        "user": relationship(
            User,
            back_populates="posts",
        ),
    },
)


@dataclass
class Student(Entity):
    name: str
    courses: list["Course"] = field(default_factory=list, repr=False)
    pass


student_table = Table(
    "student",
    mapper_registry.metadata,
    Column("id", INTEGER, primary_key=True, autoincrement=True),
    Column("name", String(500)),
)


@dataclass
class Course(Entity):
    name: str
    students: list["Student"] = field(default_factory=list, repr=False)
    pass


course_table = Table(
    "course",
    mapper_registry.metadata,
    Column("id", INTEGER, primary_key=True, autoincrement=True),
    Column("name", String(500)),
)


@dataclass
class StudentCourse:
    student_id: int
    course_id: int

    def __init__(self, student_id: int, course_id: int):
        self.student_id = student_id
        self.course_id = course_id

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return (
                self.student_id == other.student_id
                and self.course_id == other.course_id
            )
        return False

    def __hash__(self):
        return hash((self.student_id, self.course_id))


student_course_table = Table(
    "student_course",
    mapper_registry.metadata,
    Column("student_id", INTEGER, ForeignKey("student.id"), primary_key=True),
    Column("course_id", INTEGER, ForeignKey("course.id"), primary_key=True),
)

mapper_registry.map_imperatively(
    Student,
    student_table,
    properties={
        "courses": relationship(
            "Course",
            secondary=student_course_table,
            back_populates="students",
        )
    },
)
mapper_registry.map_imperatively(
    Course,
    course_table,
    properties={
        "students": relationship(
            "Student",
            secondary=student_course_table,
            back_populates="courses",
        )
    },
)
mapper_registry.map_imperatively(
    StudentCourse,
    student_course_table,
)
