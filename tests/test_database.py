from typing import cast
import random
from faker import Faker

import pytest
from sqlalchemy import ColumnElement, select, text, CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..app.sql import (
    Course,
    Location,
    Point,
    Post,
    Room,
    RoomStatus,
    Student,
    StudentCourse,
    User,
)


@pytest.mark.asyncio
async def test_user_can_be_created(db_session: AsyncSession):
    insert_statement = """
        INSERT INTO users (
      name
    ) VALUES
      ('A'),
      ('B'),
      ('C')
        """
    res = await db_session.execute(text(insert_statement))
    res = cast(CursorResult, res)
    print(res.rowcount)

    stmt = select(User)
    print(stmt)
    res = await db_session.execute(stmt)
    res = list(res.scalars().all())
    expected = [
        User(user_id=1, name="A"),
        User(user_id=2, name="B"),
        User(user_id=3, name="C"),
    ]

    print("--" * 10)
    # temp = res[0]
    # print(temp.posts)
    print("--" * 10)
    # print(expected)

    assert res == expected


# pass


@pytest.mark.asyncio
async def test_user_can_save_session(db_session: AsyncSession):
    new_user = User(user_id=10, name="Abella", posts=[Post(1, "A")])
    db_session.add(new_user)
    await db_session.commit()

    stmt = select(User).where(cast(ColumnElement[bool], User.user_id == 10))
    res = await db_session.execute(stmt)
    res = res.unique().scalars().first()

    print("--" * 50)
    print(res)

    assert res == new_user


@pytest.mark.asyncio
async def test_user_post(db_session: AsyncSession):
    new_user = User(5, "abel")

    db_session.add(new_user)
    await db_session.flush()

    new_post = Post(1, "A", new_user.user_id)
    db_session.add(new_post)

    await db_session.commit()

    stmt = select(Post)
    res = await db_session.execute(stmt)
    db_post = res.scalars().first()

    assert db_post

    print("--" * 10)
    print(db_post)
    print(db_post.user.posts)
    # print(db_post.user)
    # assert db_user == new_user

    # post_stmt = select(Post)
    # res = await db_session.execute(post_stmt)
    # db_post = res.scalars().first()

    # assert db_post

    # print(db_post.user)


@pytest.mark.asyncio
async def test_room(db_session: AsyncSession):
    new_room = Room(name="Abella", room_status=RoomStatus.PENDING)
    # new_room = Room(name="Abella")
    db_session.add(new_room)
    await db_session.commit()

    stmt = select(Room)
    res = await db_session.execute(stmt)
    res = list(res.scalars().all())

    print(res)
    print(res[0].room_status)
    assert res == [new_room]


@pytest.mark.asyncio
async def test_relation(db_session: AsyncSession):
    # new_room = Room(name="Abella", room_status=RoomStatus.PENDING)
    # t1 = datetime.now(tz=UTC)
    # t2 = datetime.now(tz=UTC)
    # new_reservation = Reservation(room=new_room, date_in=t1, date_out=t2)
    # db_session.add(new_reservation)
    # await db_session.commit()

    stmt = select(Room)
    res = await db_session.execute(stmt)
    res = list(res.unique().scalars().all())

    db_room: Room = res[0]

    print("----" * 10)
    # print(res[0].reser)
    # print(db_room.reservations)
    assert db_room.reservations
    print(db_room.reservations[0].room)
    # assert new_reservation == db_room.reservations[0]
    # assert new_room == db_room


@pytest.mark.asyncio
async def test_location(db_session: AsyncSession):
    new_location = Location(Point(1, 2), Point(3, 4))
    db_session.add(new_location)
    await db_session.commit()

    stmt = select(Location).where(Location.p1 == Point(1, 2))

    res = await db_session.execute(stmt)
    res = list(res.scalars().all())

    print(res)


@pytest.mark.asyncio
async def test_user_post_relation(db_session: AsyncSession):
    stmt = text(
        """
            insert into users (name) values ('newram');
        """
    )
    res = await db_session.execute(stmt)
    await db_session.commit()
    res = cast(CursorResult, res)

    assert res.rowcount == 1

    stmt = text(
        """
        insert into post (title, user_id) values ('new post', 1);
        """
    )
    res = await db_session.execute(stmt)
    await db_session.commit()
    res = cast(CursorResult, res)

    print("---" * 10)

    stmt = select(User).options(selectinload(User.posts))

    res = await db_session.execute(stmt)
    db_user = res.unique().scalars().first()
    assert db_user
    print(db_user.posts[0].user.posts)

    stmt = select(Post).options(selectinload(Post.user))
    print(stmt)
    res = await db_session.execute(stmt)
    db_post = res.scalars().first()
    assert db_post
    print("***" * 10)
    assert db_post
    assert db_post.user
    assert db_post.user.posts


random.seed(0)


def fake_course_name():
    adjectives = ["Introduction", "Advanced", "Fundamental"]
    subjects = ["Python", "C++", "Web", "AI", "SQL"]
    levels = ["Beginner", "Intermediate", "Advanced"]

    course_name = f"{random.choice(adjectives)} {random.choice(subjects)} {random.choice(levels)} Course"
    return course_name


@pytest.mark.asyncio
async def test_student_course(db_session: AsyncSession, fake: Faker):
    courses = [Course(fake_course_name()) for _ in range(5)]
    students = [Student(fake.name()) for _ in range(5)]
    rls = [StudentCourse(1, 1)]
    db_session.add_all(courses)
    db_session.add_all(students)
    db_session.add_all(rls)

    await db_session.commit()


@pytest.mark.asyncio
async def test_many_to_many(db_session: AsyncSession):
    print("..")
    stmt = select(Student).options(selectinload(Student.courses))
    # print(stmt)
    # res = await db_session.execute(stmt)
    # db_students = list(res.unique().scalars().all())
    # print(db_students[0].courses)
    # assert db_students[0].courses[0]

    stmt = select(Course).options(selectinload(Course.students))

    res = await db_session.execute(stmt)
    db_courses = list(res.unique().scalars().all())
    print(db_courses[0].students[0])
    assert db_courses[0]
    # pass
