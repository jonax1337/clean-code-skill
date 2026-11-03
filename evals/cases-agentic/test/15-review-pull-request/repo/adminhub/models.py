import sqlite3
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class User:
    id: int
    email: str
    name: str
    role: str
    active: bool
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "User":
        return cls(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            role=row["role"],
            active=bool(row["active"]),
            created_at=row["created_at"],
        )

    def to_dict(self) -> dict:
        return asdict(self)
