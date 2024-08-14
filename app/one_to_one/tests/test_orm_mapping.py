from faker import Faker
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.one_to_one.entities import UserEntity


@pytest.mark.asyncio
async def test_1(db_session: AsyncSession, fake: Faker):
    user = UserEntity(name="abel")
    print(user)


@pytest.mark.asyncio
async def test_2(db_session: AsyncSession):
    print(db_session)
    pass
