from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    file: str
    line: str
    column: str
