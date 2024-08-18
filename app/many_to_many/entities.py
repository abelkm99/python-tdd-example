import uuid
from dataclasses import dataclass, field

from sqlalchemy import Column, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import registry, relationship

# Register the SQLAlchemy
MapperRegistry = registry()

# ------------ Domain Models -----------
"""
4. Many-to-Many Relationship
Tables: Student, Course, and Enrollment (junction table)
    Relationships: A Student can enroll in many Courses, and a Course can have many Students.
    What to Show:
        How to set up the many-to-many relationship using an association/junction table.
        How to add, remove, and query related records.
        Handling the creation and deletion of associations.

This example doesn't show the association table examples
"""


@dataclass(kw_only=True)
class StudentEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str
    courses: list["CourseEntity"] = field(default_factory=list, repr=False)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name


@dataclass(kw_only=True)
class CourseEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str
    students: list["StudentEntity"] = field(default_factory=list, repr=False)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name


@dataclass(kw_only=True)
class EnrollmentEntity:
    course_id: uuid.UUID
    student_id: uuid.UUID


# ------------- Daabase Tables -------

StudentTable = Table(
    "student",
    MapperRegistry.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, nullable=False),
    Column("name", String(100), nullable=False),
)

CourseTable = Table(
    "course",
    MapperRegistry.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, nullable=False),
    Column("name", String(100), nullable=False),
)

EnrollmentTable = Table(
    "enrollment",
    MapperRegistry.metadata,
    Column(
        "course_id",
        Uuid(as_uuid=True),
        ForeignKey("course.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "student_id",
        Uuid(as_uuid=True),
        ForeignKey("student.id"),
        primary_key=True,
        nullable=False,
    ),
)


# ORM Mapping.

MapperRegistry.map_imperatively(
    StudentEntity,
    StudentTable,
    properties={
        "id": StudentTable.c.id,
        "name": StudentTable.c.name,
        "courses": relationship(
            CourseEntity,
            secondary=EnrollmentTable,
            back_populates="students",
        ),
    },
)

MapperRegistry.map_imperatively(
    CourseEntity,
    CourseTable,
    properties={
        "id": CourseTable.c.id,
        "name": CourseTable.c.name,
        "students": relationship(
            StudentEntity,
            secondary=EnrollmentTable,
            back_populates="courses",
        ),
    },
)

MapperRegistry.map_imperatively(
    EnrollmentEntity,
    EnrollmentTable,
    properties={
        "course_id": EnrollmentTable.c.course_id,
        "student_id": EnrollmentTable.c.student_id,
    },
)
