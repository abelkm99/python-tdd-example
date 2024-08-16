import uuid
from dataclasses import dataclass, field

from sqlalchemy import INTEGER, UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import registry, relationship

# Register the SQLAlchemy ORM
MapperRegistry = registry()

# ------------ Domain Models -----------

"""
One-to-One Relationship
------------------------
Tables: User and Profile
Relationships: Each User has one Profile, and each Profile is associated with one User.
What to Show:
    - How to create the one-to-one relationship.
    - How to access the related Profile from a User instance and vice versa.
    - How to handle cascading deletes.
"""


@dataclass(kw_only=True)
class UserEntity:
    id: uuid.UUID = field(
        default_factory=uuid.uuid4
    )  # UUID is auto-generated for each User
    name: str

    # The `profile` field represents the one-to-one relationship with `ProfileEntity`
    profile: "ProfileEntity | None" = field(
        default=None, repr=False
    )  # The profile is optional

    social_medias: list["SocialMediaEntity"] = field(default_factory=list)


@dataclass(kw_only=True)
class ProfileEntity:
    id: uuid.UUID = field(
        default_factory=uuid.uuid4
    )  # UUID is auto-generated for each Profile
    profile_picture: str
    user_id: uuid.UUID | None = field(
        default=None, repr=False
    )  # Foreign key reference to the User

    # The `user` field represents the back-reference to the User associated with this Profile
    user: "UserEntity | None" = field(init=False, repr=False)


@dataclass(kw_only=True)
class SocialMediaEntity:
    user_id: uuid.UUID
    social_media: str


# --------------- ORM MAPPING ----------------

# Define the `user` table
UserTable = Table(
    "user",
    MapperRegistry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    ),
    Column("name", String, nullable=False),
)

# Define the `profile` table
ProfileTable = Table(
    "profile",
    MapperRegistry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    ),
    Column("profile_picture", String, nullable=False),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),  # Foreign key with cascading delete
        nullable=True,  # Optional relationship
        unique=True,  # Enforces one-to-one relationship
    ),
)

# this is to check if i can this data from the user
SocialMediaTable = Table(
    "social_media",
    MapperRegistry.metadata,
    Column("id", INTEGER, autoincrement=True, primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), nullable=False),
    Column("social_media", String(100), nullable=False),
)


# ------------ Mappings ------------

# Map the UserEntity class to the user table
MapperRegistry.map_imperatively(
    UserEntity,
    UserTable,
    properties={
        "id": UserTable.c.id,
        "name": UserTable.c.name,
        # One-to-one relationship; `uselist=False` ensures only one profile per user
        "profile": relationship("ProfileEntity", uselist=False, back_populates="user"),
        "social_medias": relationship(
            SocialMediaEntity
        ),  # this line must be added otherwise it will require a flush first
    },
)

# Map the ProfileEntity class to the profile table
MapperRegistry.map_imperatively(
    ProfileEntity,
    ProfileTable,
    properties={
        "id": ProfileTable.c.id,
        "profile_picture": ProfileTable.c.profile_picture,  # Custom attribute-to-column mapping
        "user": relationship(
            "UserEntity", back_populates="profile"
        ),  # Back-reference to UserEntity
    },
)

MapperRegistry.map_imperatively(
    SocialMediaEntity,
    SocialMediaTable,
    properties={
        "user_id": SocialMediaTable.c.user_id,
        "social_media": SocialMediaTable.c.social_media,
    },
)

"""
Explanation:
------------

1. `default_factory=uuid.uuid4` in the dataclass field is used instead of `default=uuid.uuid4` to ensure that a new UUID is generated each time a new instance is created.

2. The `profile` field in `UserEntity` and `user` field in `ProfileEntity` represent the one-to-one relationship. These are marked as optional (`None`) but should not be set as the default value of the relationship object in the ORM mapping. Setting it as `None` might cause the foreign key to be `None`, which could lead to unexpected behavior, especially if the field is not nullable in the database schema.

3. In the `ProfileTable`, the `user_id` column is both nullable and unique. Nullable allows the creation of a profile without a user initially (useful in some scenarios), and unique enforces the one-to-one relationship.

4. The `ondelete="CASCADE"` in the `ForeignKey` ensures that when a `User` is deleted, the associated `Profile` is also deleted automatically, maintaining referential integrity.

5. The `uselist=False` parameter in the `relationship` ensures that the relationship between `User` and `Profile` is indeed one-to-one, as it prevents `User` from having multiple profiles.
"""
