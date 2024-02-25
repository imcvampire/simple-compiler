from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Location:
    file: str
    line: int
    column: int

    def __eq__(self, other: object) -> bool:
        if other is L:
            return True

        return super.__eq__(self, other)


L = Location("file", -1, -1)
