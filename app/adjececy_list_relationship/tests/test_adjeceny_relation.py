import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adjececy_list_relationship.entities import NodeEntity


@pytest.mark.asyncio
async def test_adjececy_orm_mapping(db_session: AsyncSession):
    root_node = NodeEntity(data="root")
    child_node = NodeEntity(data="child")
    grand_child_node = NodeEntity(data="grand_child")
    great_grand_child_node = NodeEntity(data="great_grand_child")

    grand_child_node.children.append(great_grand_child_node)
    child_node.children.append(grand_child_node)
    root_node.children.append(child_node)

    db_session.add(root_node)
    await db_session.commit()

    # Fetch the entire hierarchy
    hierarchy = await NodeEntity.get_hierarchy(db_session, root_node.id)

    # The result is now a list of tuples (NodeEntity, level)
    assert len(hierarchy) == 4

    loaded_node, level = hierarchy[0]
    assert loaded_node.data == "root"
    assert level == 1
    assert len(loaded_node.children) == 1

    child, child_level = next(
        (node, lvl) for node, lvl in hierarchy if node.data == "child"
    )
    assert child_level == 2
    assert child.parent.id == loaded_node.id
    assert len(child.children) == 1

    grand_child, grand_child_level = next(
        (node, lvl) for node, lvl in hierarchy if node.data == "grand_child"
    )
    assert grand_child_level == 3
    assert grand_child.parent.id == child.id
    assert len(grand_child.children) == 1

    great_grand_child, great_grand_child_level = next(
        (node, lvl) for node, lvl in hierarchy if node.data == "great_grand_child"
    )
    assert great_grand_child_level == 4
    assert great_grand_child.parent.id == grand_child.id
    assert len(great_grand_child.children) == 0
