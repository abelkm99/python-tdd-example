from typing import Callable
from faker import Faker
from sqlalchemy import select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.one_to_one.entities import ProfileEntitiy, UserEntity, UserTable

import pytest


@pytest.fixture
async def user_provider() -> Callable[[str | None], UserEntity]:
    def create_user(name: str | None):
        name = name if name else ""
        return UserEntity(name=name)

    return create_user


@pytest.mark.asyncio
async def test_user_entity_mapping(
    db_session: AsyncSession,
):
    user = UserEntity(name="abel")
    db_session.add(user)
    await db_session.commit()
    await db_session.reset()

    db_user = await db_session.get(UserEntity, user.id)
    assert db_user
    assert db_user.name == user.name


@pytest.mark.asyncio
async def test_profile_entitiy_mapping(db_session: AsyncSession, fake: Faker):
    profile = ProfileEntitiy(profile_picture=fake.image_url())
    db_session.add(profile)
    await db_session.commit()
    await db_session.reset()

    profile_db = await db_session.get(ProfileEntitiy, profile.id)
    assert profile_db


@pytest.mark.asyncio
async def test_user_profile_entitiy_orm_mapping(
    db_session: AsyncSession,
    fake: Faker,
    user_provider: Callable[[str | None], UserEntity],
):
    user = user_provider("abeni")
    profile = ProfileEntitiy(profile_picture=fake.image_url())
    # user_id is not profiles attribute but it still will work since it's python and i can create a new attribute
    # the following one is a hacky one.
    # as standard it should be generally recommended to create objects separately
    profile.user_id = user.id
    db_session.add(user)
    db_session.add(profile)
    await db_session.commit()
    await db_session.reset()

    stmt = (
        select(UserEntity)
        .options(selectinload(UserEntity.profile))  # type: ignore
        .where(UserTable.c.id == user.id)
    )
    res = (await db_session.execute(stmt)).scalar_one_or_none()
    assert res
    assert res.profile
    assert res.profile.user


@pytest.mark.asyncio
async def test_profile_object_can_be_created_by_passing_the_object_from_the_user_objec(
    db_session: AsyncSession,
    fake: Faker,
):
    user = UserEntity(name="abel", profile=ProfileEntitiy(profile_picture=fake.url()))
    db_session.add(user)
    await db_session.commit()
    await db_session.reset()

    stmt = (
        select(UserEntity)
        .options(selectinload(UserEntity.profile))  # type: ignore
        .where(UserTable.c.id == user.id)
    )
    res = (await db_session.execute(stmt)).scalar_one_or_none()
    assert res
    assert res.profile
    assert res.profile.user


@pytest.mark.asyncio
async def test_profile_object_can_fetch_but_doesnt_throw_erros_when_user_attibute_is_called(
    db_session: AsyncSession,
    fake: Faker,
):
    user = UserEntity(name="abel", profile=ProfileEntitiy(profile_picture=fake.url()))
    db_session.add(user)
    await db_session.commit()
    await db_session.reset()

    stmt = select(ProfileEntitiy)
    res = (await db_session.execute(stmt)).scalar_one_or_none()
    assert res

    with pytest.raises(MissingGreenlet):
        assert res.user

    # test if it can fetch it with selectinload
    stmt = select(ProfileEntitiy).options(selectinload(ProfileEntitiy.user))  # type: ignore
    res = (await db_session.execute(stmt)).scalar_one_or_none()
    assert res

    assert res.user
