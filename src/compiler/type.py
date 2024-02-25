from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    """A type."""


@dataclass(frozen=True)
class PrimitiveType(Type):
    name: str

@dataclass(frozen=True)
class ConstType(Type):
    name: str

    def __eq__(self, other: object):
        if isinstance(other, ConstType):
            return self.name == other.name
        elif isinstance(other, PrimitiveType):
            return self.name == other.name

        return False

Int = PrimitiveType("Int")
Bool = PrimitiveType("Bool")
Unit = PrimitiveType("Unit")
Func = PrimitiveType("Function")

ConstInt = ConstType("Int")
ConstBool = ConstType("Bool")
