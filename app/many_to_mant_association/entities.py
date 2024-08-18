import uuid
from dataclasses import dataclass, field

from sqlalchemy import Column, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import registry, relationship

# Register the SQLAlchemy
MapperRegistry = registry()

"""
Speaker (speakers)
    id: Primary Key
    name: Speaker's name

Conference (conferences)
    id: Primary Key
    name: Conference name

TalkAssociation (talk_association)
    speaker_id: Foreign Key to speakers table
    conference_id: Foreign Key to conferences table
    topic: The topic of the talk.
"""
# ------------ Domain Models -----------


@dataclass(kw_only=True)
class SpeakerEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str
    talks: list["TalkAssociationEntity"] = field(default_factory=list)


@dataclass(kw_only=True)
class ConferenceEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str


@dataclass(kw_only=True)
class TalkAssociationEntity:
    speaker_id: uuid.UUID
    conference_id: uuid.UUID
    topic: str

    speaker: SpeakerEntity | None = field(init=False, default=None)
    conference: ConferenceEntity | None = field(init=False, default=None)


# ------------- Database Tables -------

SpeakerTable = Table(
    "speaker",
    MapperRegistry.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, nullable=False),
    Column("name", String(100), nullable=False),
)

ConferenceTable = Table(
    "conference",
    MapperRegistry.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, nullable=False),
    Column("name", String(100), nullable=False),
)

TalkAssociationTable = Table(
    "talk_association",
    MapperRegistry.metadata,
    Column(
        "speaker_id",
        Uuid(as_uuid=True),
        ForeignKey("speaker.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "conference_id",
        Uuid(as_uuid=True),
        ForeignKey("conference.id"),
        primary_key=True,
        nullable=False,
    ),
    Column("topic", String(100), nullable=False),
)

# ------------ Orm Mapping ------------

MapperRegistry.map_imperatively(
    SpeakerEntity,
    SpeakerTable,
    properties={
        "id": SpeakerTable.c.id,
        "name": SpeakerTable.c.name,
        "talks": relationship("TalkAssociationEntity", back_populates="speaker"),
    },
)

MapperRegistry.map_imperatively(
    ConferenceEntity,
    ConferenceTable,
    properties={
        "id": ConferenceTable.c.id,
        "name": ConferenceTable.c.name,
        "talks": relationship("TalkAssociationEntity", back_populates="conference"),
    },
)

MapperRegistry.map_imperatively(
    TalkAssociationEntity,
    TalkAssociationTable,
    properties={
        "speaker_id": TalkAssociationTable.c.speaker_id,
        "conference_id": TalkAssociationTable.c.conference_id,
        "topic": TalkAssociationTable.c.topic,
        "speaker": relationship("SpeakerEntity"),
        "conference": relationship("ConferenceEntity"),
    },
)
