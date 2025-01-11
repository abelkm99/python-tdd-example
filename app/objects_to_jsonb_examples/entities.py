import dataclasses
import json
import uuid
from typing import Any

from pydantic import Field, TypeAdapter
from pydantic.dataclasses import dataclass
from sqlalchemy import UUID, Column, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import registry
from sqlalchemy.types import TypeDecorator

MapperRegistry = registry()

@dataclass
class BorrowerAdress:
    street: str = "1234 Main Street"

@dataclass(kw_only=True)
class BorrowerInfo:
    id: int
    name: str = "John Doe"
    friends: list[int] = dataclasses.field(default_factory=lambda: [0])
    age: int | None = dataclasses.field(
        default=None,
        metadata={"title": "The age of the user", "description": "do not lie!"},
    )
    height: int | None = Field(default=None, title="The height in cm", ge=50, le=300)
    address: BorrowerAdress = Field(default_factory=BorrowerAdress)


class PydanticSerializer(TypeDecorator):
    impl = JSONB
    cache_ok = True

    def __init__(self, schema, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.schema = schema

    def process_bind_param(self, value, dialect):
        if value is None:
            raise ValueError("value is None")
        return TypeAdapter(self.schema).dump_python(value)

    def process_result_value(self, value, dialect):
        if value is None:
            raise ValueError("value is None")
        return self.schema(**value)


@dataclasses.dataclass(kw_only=True)
class BorrowerEntity:
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    borrower_info: BorrowerInfo


# The rest of your code remains the same
BorrowerTable = Table(
    "borrower",
    MapperRegistry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    ),
    Column("info", PydanticSerializer(BorrowerInfo), nullable=False),
)

MapperRegistry.map_imperatively(
    BorrowerEntity,
    BorrowerTable,
    properties={
        "id": BorrowerTable.c.id,
        "borrower_info": BorrowerTable.c.info,
    },
)
