from enum import EnumMeta
from typing import Any, Type, TypeVar

ValueObjectType = TypeVar("ValueObjectType", bound="ValueObject")


class ValueObjectEnumError(Exception):
    def __str__(self):
        return "Value Object got invalid value."


class ValueObject:
    value: Any

    def __composite_values__(self):
        return (self.value,)

    @classmethod
    def from_value(cls: Type["ValueObject"], value: Any) -> "ValueObject":
        if isinstance(cls, EnumMeta):
            for item in cls:
                if item.value == value:
                    return item
            raise ValueObjectEnumError

        instance = cls(value=value)
        return instance
