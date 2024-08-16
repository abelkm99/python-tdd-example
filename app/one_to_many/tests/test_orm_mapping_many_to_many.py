from collections.abc import Callable

import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.one_to_many.entities import BookEntity, PublisherEntity, PublisherTable


# Fixture to provide a UserEntity instance
@pytest.fixture
async def publisher_provider() -> Callable[[str | None], PublisherEntity]:
    def create_user(name: str | None):
        name = name if name else ""
        return PublisherEntity(name=name)

    return create_user


@pytest.fixture
async def publisher(
    db_session: AsyncSession,
    publisher_provider: Callable[[str | None], PublisherEntity],
) -> PublisherEntity:
    new_publisher = publisher_provider("abel")
    db_session.add(new_publisher)
    await db_session.commit()
    await db_session.reset()
    return new_publisher


# Test to verify PublisherEntity mapping to the database
@pytest.mark.asyncio
async def test_publisher_entity_mapping(db_session: AsyncSession):
    # Create a new PublisherEntity
    user = PublisherEntity(name="abel")

    # Add and commit to the database session
    db_session.add(user)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # Fetch the user from the database
    db_user = await db_session.get(PublisherEntity, user.id)

    # Assertions to ensure correct mapping
    assert db_user
    assert db_user.name == user.name


# Test to verify BookEntity mapping to the database
@pytest.mark.asyncio
async def test_book_entity_mapping(
    db_session: AsyncSession,
    publisher: PublisherEntity,
):
    # Create a new BookEntity with a fake profile picture URL
    book = BookEntity(name="book name", publisher_id=publisher.id)

    # Add and commit to the database session
    db_session.add(book)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # Fetch the profile from the database
    book_db = await db_session.get(BookEntity, book.id)

    # Assertion to ensure profile was saved
    assert book_db


# # Test to verify the one-to-one relationship between UserEntity and ProfileEntity
@pytest.mark.asyncio
async def test_publisher_book_orm_mapping(
    db_session: AsyncSession,
    publisher: PublisherEntity,
):
    # Create a new UserEntity

    new_book = BookEntity(name="book1", publisher_id=publisher.id)

    # Add both entities to the session and commit
    db_session.add(new_book)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # test only getting the Publisher with out the book

    pub = await db_session.get(PublisherEntity, publisher.id)

    assert pub
    with pytest.raises(MissingGreenlet):
        """
        We want this Exception to be raised because.
        our propertires already know there is a relationship.
        so everytime we are trying to fetch that it's going to refer to the relation.
        """
        assert pub.books

    # Query to fetch the user along with the books
    stmt = (
        select(PublisherEntity)
        .options(
            selectinload(PublisherEntity.books)  # pyright: ignore[reportArgumentType]
        )  # Use selectinload to eagerly load the books
        .where(PublisherTable.c.id == publisher.id)
    )

    # Execute the query and fetch the result
    res = (await db_session.execute(stmt)).scalar_one_or_none()

    # Assertions to verify the one-to-one relationship
    assert res
    assert res.books
    assert res.books[0].name == "book1"


@pytest.mark.asyncio
async def test_publisher_book_orm_mapping_will_create_empty_list_of_user(
    db_session: AsyncSession,
    publisher: PublisherEntity,
):
    """In this test we want to check if we can actually get empty array if we don't have any relation
    """

    stmt = (
        select(PublisherEntity)
        .options(
            selectinload(PublisherEntity.books)  # pyright: ignore[reportArgumentType]
        )  # Use selectinload to eagerly load the books
        .where(PublisherTable.c.id == publisher.id)
    )

    res = (await db_session.execute(stmt)).scalar_one_or_none()

    # Assertions to verify the one-to-one relationship
    assert res
    assert res.books == []


@pytest.mark.asyncio
async def test_book_table_can_retrive_publisher(
    db_session: AsyncSession,
    publisher: PublisherEntity,
):
    book = BookEntity(name="book name", publisher_id=publisher.id)

    # Add and commit to the database session
    db_session.add(book)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # test with out selectinload option

    bk = await db_session.get(BookEntity, book.id)
    assert bk
    with pytest.raises(MissingGreenlet):
        # this exception should be raised cause i didn't lood the publisher
        assert bk.publisher

    stmt = select(BookEntity).options(
        selectinload(BookEntity.publisher)  # pyright: ignore[reportArgumentType]
    )
    result = (await db_session.execute(stmt)).scalar_one_or_none()
    assert result
    assert result.publisher
    assert result.publisher.name == "abel"


@pytest.mark.asyncio
async def test_delete_publisher_deletes_book(
    db_session: AsyncSession,
    publisher: PublisherEntity,
):
    book = BookEntity(name="book name", publisher_id=publisher.id)

    # Add and commit to the database session
    db_session.add(book)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    dlt_stmt = delete(PublisherEntity).where(PublisherTable.c.id == publisher.id)
    res = await db_session.execute(dlt_stmt)
    assert res.rowcount == 1
    await db_session.commit()

    # reset the database
    await db_session.reset()

    db_pub = await db_session.get(PublisherEntity, publisher.id)
    assert not db_pub

    db_book = await db_session.get(BookEntity, book.id)
    assert not db_book
