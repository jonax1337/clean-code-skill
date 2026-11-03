from collections import defaultdict

from tabtally.models import Expense


def net_balances(expenses: list[Expense]) -> dict[str, int]:
    """Cents each person is owed (positive) or owes (negative); the values add up to zero."""
    balances: dict[str, int] = defaultdict(int)
    for expense in expenses:
        balances[expense.payer] += expense.cents
        for person, share in expense.shares.items():
            balances[person] -= share
    return dict(balances)
