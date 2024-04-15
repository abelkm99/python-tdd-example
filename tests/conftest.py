import pytest
import pytest_asyncio
from faker import Faker
import asyncio
from sqlalchemy.exc import SQLAlchemyError
from ..app.sql import async_engine, get_db


Faker.seed(10)


@pytest.fixture(scope="session")
def fake() -> Faker:
    return Faker()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def reset_database():
    try:
        # print(mapper_registry.metadata.tables)
        async with async_engine.begin() as conn:
            # await conn.run_sync(mapper_registry.metadata.drop_all)
            # await conn.run_sync(mapper_registry.metadata.create_all)
            pass
        await async_engine.dispose()
    except Exception as e:
        raise e


@pytest_asyncio.fixture
async def db_session():
    async with get_db() as session:
        try:
            yield session
            await session.close()
        except SQLAlchemyError as e:
            await session.rollback()
            await session.close()
            raise e
