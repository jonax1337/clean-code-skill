from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    id: int
    payer: str
    description: str
    cents: int
    shares: dict[str, int]  # cents each person owes; adds up to `cents`
