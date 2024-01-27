from dataclasses import dataclass


@dataclass
class Location:
    file: str
    line: str
    column: str
