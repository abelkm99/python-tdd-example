import uuid
from dataclasses import dataclass, field

from sqlalchemy import UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import Relationship, registry, relationship

# Register the SQLAlchemy ORM
MapperRegistry = registry()

# ------------ Domain Models -----------

"""
Tables: Book and Publisher
Relationships: Each Book is published by one Publisher, but each Publisher can publish multiple Books.
What to Show:
How to map the many-to-one relationship.
How to query Books by Publisher.
Handling foreign keys and backrefs.
"""


@dataclass(kw_only=True)
class PublisherEntity:
    id: uuid.UUID = field(
        default_factory=uuid.uuid4
    )  # UUID is auto-generated for each Profile
    name: str
    books: "list[BookEntity]" = field(
        init=False,
    )  # make it an empty list if it's not fetched


@dataclass(kw_only=True)
class BookEntity:
    id: uuid.UUID = field(
        default_factory=uuid.uuid4
    )  # UUID is auto-generated for each User
    name: str
    publisher_id: uuid.UUID  # since it's a must
    publisher: PublisherEntity | None = field(
        init=False, default=None
    )  # make it optionally None cause it can not be


# --------------- ORM MAPPING ----------------

# Define the `user` table
PublisherTable = Table(
    "publisher",
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

# Define the `profile` table
BookTable = Table(
    "book",
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
    Column(
        "publisher_id",
        UUID(as_uuid=True),
        ForeignKey("publisher.id", ondelete="CASCADE"),  # we should have this one
        nullable=False,
    ),  # publisher is a must in this case
)

# ------------ Mappings ------------

# Map the PublisherEntity class to the user table
MapperRegistry.map_imperatively(
    PublisherEntity,
    PublisherTable,
    properties={
        "id": PublisherTable.c.id,
        "name": PublisherTable.c.name,
        "books": Relationship(
            BookEntity,
            back_populates="publisher",
            cascade="all, delete",
            passive_deletes=True,
        ),
    },
)

# Map the BookEntitiy class to the profile table
MapperRegistry.map_imperatively(
    BookEntity,
    BookTable,
    properties={
        "id": BookTable.c.id,
        "name": BookTable.c.name,
        "publisher": relationship(
            PublisherEntity,
            uselist=False,
            back_populates="books",
        ),
    },
)
