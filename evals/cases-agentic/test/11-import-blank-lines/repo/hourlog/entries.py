from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Entry:
    day: date
    project: str
    minutes: int

    def __post_init__(self) -> None:
        if not self.project:
            raise ValueError("project must not be empty")
        if self.minutes <= 0:
            raise ValueError("minutes must be positive")
