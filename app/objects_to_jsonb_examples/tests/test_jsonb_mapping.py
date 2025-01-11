from uuid import UUID

import pytest
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects_to_jsonb_examples.entities import BorrowerAdress, BorrowerEntity, BorrowerInfo, BorrowerTable


@pytest.mark.asyncio
async def test_add_person(db_session: AsyncSession):
    p1 = BorrowerEntity(borrower_info=BorrowerInfo(id=10))
    db_session.add(p1)
    await db_session.commit()
    await db_session.reset()

    res = await db_session.get(BorrowerEntity, p1.id)
    assert res
    assert res == p1
    res.borrower_info.age = 25
    await db_session.commit()
    await db_session.reset()
    db_session.add(res)

    res = await db_session.get(BorrowerEntity, p1.id)
    assert res
    assert res.borrower_info.age == 25


@pytest.mark.asyncio
async def test_query_by_name(db_session: AsyncSession):
    # Arrange
    test_name = "bella"
    p1 = BorrowerEntity(
        borrower_info=BorrowerInfo(id=11, name=test_name, address=BorrowerAdress()),
    )
    db_session.add(p1)
    await db_session.commit()
    await db_session.refresh(p1)

    # Act
    stmt = select(BorrowerEntity).where(BorrowerTable.c.info["name"] == test_name)

    query = await db_session.execute(stmt)
    result = query.scalars().first()

    # Assert
    assert result is not None
    assert result.borrower_info.name == test_name


@pytest.mark.asyncio
async def test_update_by_name(db_session: AsyncSession):
    initial_name = "Bob Johnson"
    new_name = "Bob_updated Johnson"
    p1 = BorrowerEntity(borrower_info=BorrowerInfo(id=12, name=initial_name))
    db_session.add(p1)
    await db_session.commit()
    await db_session.refresh(p1)

    updated_info = p1.borrower_info
    updated_info.name = new_name

    await db_session.execute(
        update(BorrowerEntity)
        .where(BorrowerTable.c.info["name"].astext == initial_name)
        .values(borrower_info=updated_info)
    )
    await db_session.commit()

    # Assert
    stmt = select(BorrowerEntity).where(BorrowerTable.c.info["name"].astext == new_name)
    query = await db_session.execute(stmt)
    result = query.scalars().first()
    assert result is not None
    assert result.borrower_info.name == new_name
