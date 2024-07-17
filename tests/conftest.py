import pytest
import pytest_asyncio
from faker import Faker
import asyncio
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..app.sql import async_engine, get_db, mapper_registry


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
            await conn.run_sync(mapper_registry.metadata.drop_all)
            await conn.run_sync(mapper_registry.metadata.create_all)
            pass
        await async_engine.dispose()
    except Exception as e:
        raise e


@pytest_asyncio.fixture()
async def db_session():
    async with get_db() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        finally:
            # Clean up database
            tables = ", ".join(
                '"' + table.name + '"'
                for table in mapper_registry.metadata.sorted_tables
            )
            query = f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE;"
            await session.execute(text(query))
            await session.commit()
            await session.close()
