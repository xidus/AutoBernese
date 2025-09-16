"""
Work with data sources and destinations

"""

from pathlib import Path


class Pair:
    fname_remote: str
    fname_local: str


class SourceDefinition:
    identifier: str
    description: str
    # May contain format fields
    url: str | Path
    filenames: list[str] | None = None
    destination: str | Path

    def pairs(self) -> list[Pair]:
        return [Pair()]
