import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_orm_mapping_associate_table(db_session: AsyncSession):
    print(db_session)
