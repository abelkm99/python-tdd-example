import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.many_to_many.entities import (
    CourseEntity,
    CourseTable,
    EnrollmentEntity,
    EnrollmentTable,
    StudentEntity,
    StudentTable,
)

"""
for many to many relation ship
I would prefer appending it to the list would be much more better 
IE: student.courses.append(course)
or course.students.append(student)

even if i am creating a new one.



# the second way that i would prefer is 
to create it with an enrollment object
new_enrollment = EnrollmentEntity(student_id=student_id, course_id=course_id)
"""


@pytest.mark.asyncio
async def test_student_table_orm_maaping_works(db_session: AsyncSession):
    student = StudentEntity(name="abel")
    course = CourseEntity(name="biology")

    db_session.add(student)
    db_session.add(course)
    await db_session.commit()

    await db_session.reset()

    db_student = await db_session.get(StudentEntity, student.id)
    assert db_student
    assert db_student.id == student.id
    assert db_student.name == student.name

    db_course = await db_session.get(CourseEntity, course.id)
    assert db_course
    assert db_course.id == course.id
    assert db_course.name == course.name


@pytest.mark.asyncio
async def test_orm_mapping_works_by_just_appending(db_session: AsyncSession):
    student = StudentEntity(name="abel")
    course = CourseEntity(name="biology")
    student.courses.append(course)
    db_session.add(student)
    await db_session.commit()
    await db_session.reset()

    # how do i check it it
    stmt = select(EnrollmentEntity).where(
        EnrollmentTable.c.student_id == student.id,
        EnrollmentTable.c.course_id == course.id,
    )
    res = await db_session.execute(stmt)
    res = res.scalar_one_or_none()
    assert res
    assert res.course_id == course.id
    assert res.student_id == student.id

    # fetch the student and the courses they are learning.
    stmt = (
        select(StudentEntity)
        .options(
            selectinload(StudentEntity.courses)  # pyright: ignore[reportArgumentType]
        )
        .where(StudentTable.c.id == student.id)
    )
    db_student = (await db_session.execute(stmt)).scalar_one_or_none()
    assert db_student
    assert db_student
    assert db_student.courses
    assert db_student.courses[0].name == "biology"

    await db_session.reset()

    # check i can get the course and the students
    stmt = (
        select(CourseEntity)
        .options(
            selectinload(CourseEntity.students)  # pyright: ignore[reportArgumentType]
        )
        .where(CourseTable.c.id == course.id)
    )
    db_course = (await db_session.execute(stmt)).scalar_one_or_none()
    assert db_course
    assert db_course.name == "biology"
    assert db_course.students
    assert db_course.students[0].name == "abel"


@pytest.mark.asyncio
async def test_orm_mapping_works_by_just_using_the_relation(db_session: AsyncSession):
    student = StudentEntity(name="abel")
    bio = CourseEntity(name="biology")
    math = CourseEntity(name="math")
    physics = CourseEntity(name="physics ")
    enrollments = [
        EnrollmentEntity(course_id=bio.id, student_id=student.id),
        EnrollmentEntity(course_id=math.id, student_id=student.id),
    ]
    db_session.add(student)  # add the student
    db_session.add_all([bio, math, physics])  # add the courses
    await db_session.flush()
    db_session.add_all(enrollments)  # add the student's relationship

    await db_session.commit()
    await db_session.reset()

    stmt = select(EnrollmentEntity).where(
        EnrollmentTable.c.student_id == student.id,
        EnrollmentTable.c.course_id == math.id,
    )
    res = await db_session.execute(stmt)
    res = res.scalar_one_or_none()
    assert res
    assert res.course_id == math.id
    assert res.student_id == student.id

    # fetch students from the course table.

    await db_session.reset()

    # check i can get the course and the students
    stmt = (
        select(CourseEntity)
        .options(
            selectinload(CourseEntity.students)  # pyright: ignore[reportArgumentType]
        )
        .where(CourseTable.c.id == math.id)
    )
    db_course = (await db_session.execute(stmt)).scalar_one_or_none()
    assert db_course
    assert db_course.name == "math"
    assert db_course.students
    assert db_course.students[0].name == "abel"

    # fetch student abels registered courses

    await db_session.reset()

    stmt = (
        select(StudentEntity)
        .options(
            selectinload(
                StudentEntity.courses,  # pyright: ignore[reportArgumentType]
            )
        )
        .where(StudentTable.c.name == "abel")
    )
    print(stmt)
    db_student = (await db_session.execute(stmt)).scalar_one_or_none()
    assert db_student
    assert db_student.name == "abel"
    assert math in db_student.courses
    assert bio in db_student.courses
    assert physics not in db_student.courses
