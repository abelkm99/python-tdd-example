from collections.abc import Callable

import pytest
from faker import Faker
from sqlalchemy import delete, select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.one_to_one.entities import (
    ProfileEntity,
    SocialMediaEntity,
    UserEntity,
    UserTable,
)


# Fixture to provide a UserEntity instance
@pytest.fixture
async def user_provider() -> Callable[[str | None], UserEntity]:
    def create_user(name: str | None):
        name = name if name else ""
        return UserEntity(name=name)

    return create_user


# Test to verify UserEntity mapping to the database
@pytest.mark.asyncio
async def test_user_entity_mapping(db_session: AsyncSession):
    # Create a new UserEntity
    user = UserEntity(name="abel")

    # Add and commit to the database session
    db_session.add(user)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # Fetch the user from the database
    db_user = await db_session.get(UserEntity, user.id)

    # Assertions to ensure correct mapping
    assert db_user
    assert db_user.name == user.name


# Test to verify ProfileEntity mapping to the database
@pytest.mark.asyncio
async def test_profile_entity_mapping(db_session: AsyncSession, fake: Faker):
    # Create a new ProfileEntity with a fake profile picture URL
    profile = ProfileEntity(profile_picture=fake.image_url())

    # Add and commit to the database session
    db_session.add(profile)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # Fetch the profile from the database
    profile_db = await db_session.get(ProfileEntity, profile.id)

    # Assertion to ensure profile was saved
    assert profile_db


# Test to verify the one-to-one relationship between UserEntity and ProfileEntity
@pytest.mark.asyncio
async def test_user_profile_entity_orm_mapping(
    db_session: AsyncSession,
    fake: Faker,
    user_provider: Callable[[str | None], UserEntity],
):
    # Create a new UserEntity
    user = user_provider("abeni")

    # Create a new ProfileEntity with a fake profile picture URL
    profile = ProfileEntity(profile_picture=fake.image_url(), user_id=user.id)

    # Add both entities to the session and commit
    db_session.add(user)
    db_session.add(profile)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # Query to fetch the user along with their profile
    stmt = (
        select(UserEntity)
        .options(
            selectinload(UserEntity.profile)  # pyright: ignore[reportArgumentType]
        )  # Use selectinload to eagerly load the profile
        .where(UserTable.c.id == user.id)
    )

    # Execute the query and fetch the result
    res = (await db_session.execute(stmt)).scalar_one_or_none()

    # Assertions to verify the one-to-one relationship
    assert res
    assert res.profile
    assert res.profile.user


# Test to verify that a ProfileEntity can be created by directly passing it to a UserEntity
@pytest.mark.asyncio
async def test_profile_object_can_be_created_by_passing_the_object_from_the_user_object(
    db_session: AsyncSession,
    fake: Faker,
):
    # Create a new UserEntity and directly associate a ProfileEntity with it
    user = UserEntity(name="abel", profile=ProfileEntity(profile_picture=fake.url()))

    # Add the user (and implicitly the profile) to the session and commit
    db_session.add(user)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # Query to fetch the user along with their profile
    stmt = (
        select(UserEntity)
        .options(
            selectinload(UserEntity.profile)  # pyright: ignore[reportArgumentType]
        )  # Use selectinload to eagerly load the profile
        .where(UserTable.c.id == user.id)
    )

    # Execute the query and fetch the result
    res = (await db_session.execute(stmt)).scalar_one_or_none()

    # Assertions to ensure correct mapping and relationships
    assert res
    assert res.profile
    assert res.profile.user


# Test to verify that a ProfileEntity can fetch its related UserEntity without throwing an error
@pytest.mark.asyncio
async def test_profile_object_can_fetch_but_doesnt_throw_errors_when_user_attribute_is_called(
    db_session: AsyncSession,
    fake: Faker,
):
    # Create a new UserEntity and directly associate a ProfileEntity with it
    user = UserEntity(name="abel", profile=ProfileEntity(profile_picture=fake.url()))

    # Add the user (and implicitly the profile) to the session and commit
    db_session.add(user)
    await db_session.commit()

    # Reset session to simulate a new transaction
    await db_session.reset()

    # Query to fetch the profile
    stmt = select(ProfileEntity)
    res = (await db_session.execute(stmt)).scalar_one_or_none()

    # Ensure that the profile was fetched
    assert res

    # Attempt to access the associated user without eager loading (will raise MissingGreenlet)
    with pytest.raises(MissingGreenlet):
        assert res.user

    # Now fetch the profile along with the associated user using selectinload
    stmt = select(ProfileEntity).options(
        selectinload(ProfileEntity.user)  # pyright: ignore[reportArgumentType]
    )  # Use selectinload to load user
    res = (await db_session.execute(stmt)).scalar_one_or_none()

    # Assertions to ensure the user was fetched correctly
    assert res
    assert res.user


# test deleting will cause
@pytest.mark.asyncio
async def test_deleting_user_will_delete_profile(db_session: AsyncSession, fake: Faker):
    # Create a new UserEntity and directly associate a ProfileEntity with it
    profile = ProfileEntity(profile_picture=fake.url())
    user = UserEntity(name="abel", profile=profile)
    # Add the user (and implicitly the profile) to the session and commit
    db_session.add(user)
    await db_session.commit()
    # Reset session to simulate a new transaction
    await db_session.reset()
    # Query to fetch the user along with their profile
    assert await db_session.get(ProfileEntity, profile.id)
    assert await db_session.get(UserEntity, user.id)

    await db_session.reset()
    # Delete the user
    dlt_stmt = delete(UserEntity).where(UserTable.c.id == user.id)
    res = await db_session.execute(dlt_stmt)
    assert res.rowcount == 1
    await db_session.commit()
    # Commit the deletion
    # Reset session to simulate a new transaction
    await db_session.reset()
    # Attempt to fetch the user and profile
    assert not await db_session.get(UserEntity, user.id)
    assert not await db_session.get(ProfileEntity, profile.id)


@pytest.mark.asyncio
async def test_user_profile_and_multiple_social_media_mapping_works_and_chec_nav(
    db_session: AsyncSession,
    fake: Faker,
):
    # Create a new UserEntity and directly associate a ProfileEntity with it
    user = UserEntity(name="abel", profile=ProfileEntity(profile_picture=fake.url()))
    social_medias = [
        SocialMediaEntity(social_media=fake.url(), user_id=user.id),
        SocialMediaEntity(social_media=fake.url(), user_id=user.id),
        SocialMediaEntity(social_media=fake.url(), user_id=user.id),
    ]

    # Add the user (and implicitly the profile) to the session and commit
    db_session.add(user)
    db_session.add_all(social_medias)
    await db_session.commit()

    await db_session.reset()

    stmt = select(ProfileEntity).options(
        selectinload(ProfileEntity.user).selectinload(
            UserEntity.social_medias  # pyright: ignore[reportArgumentType]
        )
    )
    res = (await db_session.execute(stmt)).scalar_one_or_none()

    assert res

    assert res.user
    assert res.user.social_medias
