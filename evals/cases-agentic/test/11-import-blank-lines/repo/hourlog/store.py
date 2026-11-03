"""The log file: JSON with one list of entries."""

import json
from datetime import date
from pathlib import Path

from hourlog.entries import Entry


def load(path: Path) -> list[Entry]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Entry(date.fromisoformat(item["day"]), item["project"], item["minutes"]) for item in raw["entries"]]


def save(path: Path, entries: list[Entry]) -> None:
    items = [{"day": entry.day.isoformat(), "project": entry.project, "minutes": entry.minutes} for entry in entries]
    path.write_text(json.dumps({"entries": items}, indent=2) + "\n", encoding="utf-8")


def append(path: Path, new_entries: list[Entry]) -> None:
    save(path, [*load(path), *new_entries])
