from typing import Annotated, NamedTuple
import msgspec


class User(msgspec.Struct):
    name: str
    groups: set[str]
    email: str | None = None


alice = User("alice", groups={"admin", "engineering"})

print(alice)

msg = msgspec.msgpack.encode(alice)

print(msg)

decoder = msgspec.json.Decoder(User)
decoder.decode(msg)
msgspec.json.decode(msg, type=User)

loaded = decoder.decode(
    '{"name":"alice","groups":["admin","engineering"],"email":"1"}',
)


msgspec.json.decode(b"1", type=bool, strict=False)
msgspec.json.decode(b'"FaLsE"', type=bool, strict=False)


class Employee(NamedTuple):
    name: str
    id: int


employee = Employee("alice", 1)
msgspec.json.encode(employee)


class Get(msgspec.Struct):
    id: Annotated[int, msgspec.Meta(gt=0)]
    name: Annotated[str, msgspec.Meta(pattern="^[a-z0-9_]*$")]


temp = msgspec.json.encode(Get(1, "?abel"))

msgspec.json.decode(temp, type=Get)

PositiveFloat = Annotated[float, msgspec.Meta(gt=0, description="something")]


class Dimensions(msgspec.Struct):
    """Dimensions for a product, all measurements in centimeters"""

    length: PositiveFloat
    width: PositiveFloat
    height: PositiveFloat


class Product(msgspec.Struct):
    """A product in a catalog"""

    id: int
    name: str
    price: PositiveFloat
    tags: set[str] = set()
    dimensions: Dimensions | None = None


schema = msgspec.json.schema(list[Product])

print(schema)

temp = """Todo
    Tuesday
    - Finish the Domain Layer + repository Layer for the Users Module + Test
    Wednesday
    - Finish the Service + dependency injection +  sqlalchemy for the user module
    - Finish the test
    Tuesday:
        Persona package will be started by euael.
        Chat Package will be started by abel.
        We will also do possible schema change on the database for this two package such as support for more models, multiple group chat
"""
