"""Read time entries from a CSV export: one `date,project,minutes` per line."""

from collections.abc import Iterable
from datetime import date

from hourlog.entries import Entry


class ImportFormatError(ValueError):
    """A line of the import file cannot be read; the message names the line."""


def parse_entries(lines: Iterable[str]) -> list[Entry]:
    entries = []
    for number, line in enumerate(lines, start=1):
        try:
            entries.append(_parse_line(line))
        except ValueError as error:
            raise ImportFormatError(f"line {number}: {error}") from error
    return entries


def _parse_line(line: str) -> Entry:
    day, project, minutes = line.rstrip("\r\n").split(",")
    return Entry(date.fromisoformat(day.strip()), project.strip(), int(minutes))
