from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Location:
    file: str
    line: str
    column: str

    def __eq__(self, other: Location) -> bool:
        if other == L:
            return True

        return super.__eq__(self, other)


L = Location("file", "line", "column")
