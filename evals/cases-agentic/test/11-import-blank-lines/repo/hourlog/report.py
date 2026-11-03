from hourlog.entries import Entry


def totals_by_project(entries: list[Entry]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for entry in entries:
        totals[entry.project] = totals.get(entry.project, 0) + entry.minutes
    return totals


def format_duration(minutes: int) -> str:
    hours, rest = divmod(minutes, 60)
    return f"{hours}h{rest:02d}"
