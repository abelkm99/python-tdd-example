import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.many_to_many_association.entities import (
    ConferenceEntity,
    SpeakerEntity,
    SpeakerTable,
    TalkAssociationEntity,
    TalkAssociationTable,
)


@pytest.mark.asyncio
async def test_associated_table_orm_maping(db_session: AsyncSession):
    speaker = SpeakerEntity(name="abel")
    conference = ConferenceEntity(name="PyCon")
    association = TalkAssociationEntity(
        speaker_id=speaker.id,
        conference_id=conference.id,
        topic="Python",
    )
    db_session.add(speaker)
    db_session.add(conference)
    db_session.add(association)

    await db_session.commit()
    await db_session.reset()

    # Run the test

    stmt = (
        select(
            SpeakerEntity,
            TalkAssociationEntity,  # if we want to fetch the conference as well
        )
        .join(
            TalkAssociationEntity,
            TalkAssociationTable.c.speaker_id == SpeakerTable.c.id,
        )
        .options(
            selectinload(SpeakerEntity.talks),  # pyright: ignore[reportArgumentType]
        )
        .options(
            selectinload(
                TalkAssociationEntity.conference  # pyright: ignore[reportArgumentType]
            ),
        )
        .where(SpeakerTable.c.id == speaker.id)
    )

    db_speaker = (await db_session.execute(stmt)).scalars().first()
    assert db_speaker
    assert db_speaker.talks
    assert db_speaker.talks[0].topic == "Python"
    assert db_speaker.talks[0].speaker

    assert db_speaker.talks[0].speaker.id == speaker.id
    assert db_speaker.talks[0].conference
    assert db_speaker.talks[0].conference.name == "PyCon"
