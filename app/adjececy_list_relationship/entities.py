from typing import List
import uuid
from dataclasses import dataclass, field

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Uuid,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, registry, relationship, selectinload

# Register the SQLAlchemy
MapperRegistry = registry()


# ------ Domain Model ------
@dataclass(kw_only=True)
class NodeEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    parent_id: uuid.UUID | None = None
    data: str
    children: List["NodeEntity"] = field(
        default_factory=list, compare=False, repr=False
    )

    @classmethod
    async def get_hierarchy(cls, session: AsyncSession, root_id: uuid.UUID):
        cte = (
            select(
                NodeTable.c.id,
                NodeTable.c.parent_id,
                NodeTable.c.data,
                func.cast(1, Integer).label("level"),
            )
            .where(NodeTable.c.id == root_id)
            .cte(recursive=True, name="cte")
        )

        cte = cte.union_all(
            select(
                NodeTable.c.id,
                NodeTable.c.parent_id,
                NodeTable.c.data,
                (cte.c.level + 1).label("level"),
            ).join(cte, NodeTable.c.parent_id == cte.c.id)
        )

        aliased_cte = aliased(cte, name="aliased_cte")

        stmt = (
            select(NodeEntity, aliased_cte.c.level)
            .join(aliased_cte, NodeEntity.id == aliased_cte.c.id)
            .options(selectinload(NodeEntity.children))
            .order_by(aliased_cte.c.level, aliased_cte.c.id)
        )

        result = await session.execute(stmt)
        return result.unique().all()


# ------ Database Table ------

NodeTable = Table(
    "node",
    MapperRegistry.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, nullable=False),
    Column("parent_id", Uuid(as_uuid=True), ForeignKey("node.id"), nullable=True),
    Column("data", String(50), nullable=False),
)

# ------ Relationships ------
MapperRegistry.map_imperatively(
    NodeEntity,
    NodeTable,
    properties={
        "children": relationship(
            "NodeEntity",
            back_populates="parent",
            cascade="all, delete-orphan",
            collection_class=list,
        ),
        "parent": relationship(
            "NodeEntity",
            back_populates="children",
            remote_side=[NodeTable.c.id],
        ),
    },
)
