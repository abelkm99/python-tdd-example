import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.one_to_one.entities import MapperRegistry

Faker.seed(10)


database_url = "postgresql+asyncpg://root:123456789@localhost:5432/example"
async_engine = create_async_engine(
    url=database_url,
    future=True,
    pool_size=20,
    max_overflow=20,
    # echo=True,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


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
        async with async_engine.begin() as conn:
            await conn.run_sync(MapperRegistry.metadata.drop_all)
            await conn.run_sync(MapperRegistry.metadata.create_all)
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
                for table in MapperRegistry.metadata.sorted_tables
            )
            query = f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE;"
            await session.execute(text(query))
            await session.commit()
            await session.close()
