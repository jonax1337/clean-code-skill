from tabtally.balances import net_balances
from tabtally.models import Expense


def test_payer_is_owed_what_the_others_share():
    expense = Expense(1, "alice", "Pizza", 3000, {"alice": 1000, "bob": 1000, "carol": 1000})
    assert net_balances([expense]) == {"alice": 2000, "bob": -1000, "carol": -1000}


def test_balances_add_up_to_zero_over_several_expenses():
    expenses = [
        Expense(1, "alice", "Pizza", 3000, {"alice": 1000, "bob": 1000, "carol": 1000}),
        Expense(2, "bob", "Taxi", 1001, {"alice": 501, "bob": 500}),
    ]
    assert sum(net_balances(expenses).values()) == 0


def test_no_expenses_means_no_balances():
    assert net_balances([]) == {}
