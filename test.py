from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from msgspec import Struct
from sqlalchemy import Column, Integer, String, Table

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import registry

database_url = "postgresql+asyncpg://root:123456789@localhost:5432/example"
async_engine = create_async_engine(
    url=database_url,
    future=True,
    pool_size=20,
    max_overflow=20,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


mapper_registry = registry()


studentTable = Table(
    "student_table",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)


class Student(Struct):
    id: int
    name: str


mapper_registry.map_imperatively(Student, studentTable)


# async def main():

#     async with async_engine.begin() as conn:
#         await conn.run_sync(mapper_registry.metadata.drop_all)
#         await conn.run_sync(mapper_registry.metadata.create_all)

#     async with get_db() as db_session:
#         # add temp students
#         st = Student(id=1, name="abel")
#         db_session.add(st)
#         await db_session.commit()

#         # stmt = select(Student)
#         # res = await db_session.execute(stmt)
#         # students = res.scalars().all()
#         # print(students)


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(main())
