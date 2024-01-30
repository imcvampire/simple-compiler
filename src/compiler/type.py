from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    """A type."""


@dataclass(frozen=True)
class PrimitiveType(Type):
    name: str


Int = PrimitiveType("Int")
Bool = PrimitiveType("Bool")
Unit = PrimitiveType("Unit")
Function = PrimitiveType("Function")
