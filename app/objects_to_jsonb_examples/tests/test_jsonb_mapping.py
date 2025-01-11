from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects_to_jsonb_examples.entities import BorrowerEntity, BorrowerInfo


@pytest.mark.asyncio
async def test_add_person(db_session: AsyncSession):
    p1 = BorrowerEntity(borrower_info=BorrowerInfo(id=10))
    db_session.add(p1)
    await db_session.commit()
    await db_session.reset()

    res = await db_session.get(BorrowerEntity, p1.id)
    assert res
    assert res == p1
    res.id = UUID("38c002d3-975e-4479-b637-159202c8acdd")
    res.borrower_info.age = 25

    print(db_session.is_modified(res))
