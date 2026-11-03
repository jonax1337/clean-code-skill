import math
from decimal import Decimal
from fractions import Fraction

import pytest

from tabtally.cli import main

ADD = ["add", "--paid-by", "zed", "--description", "Dinner"]


@pytest.fixture
def run(tmp_path, capsys):
    def invoke(*argv):
        try:
            code = main(["--file", str(tmp_path / "tabtally.json"), *argv])
        except SystemExit as exit_request:  # argparse reports usage errors this way
            code = exit_request.code
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return invoke


def balances_in_cents(run):
    _, out, _ = run("balances")
    return {name: int(Decimal(amount) * 100) for name, amount in (line.split() for line in out.splitlines())}


def cents_of(amount):
    return int(Decimal(amount) * 100)


def percent_options(percents):
    return [option for name, pct in percents.items() for option in ("--percent", f"{name}={pct}")]


SPLITS = [
    ("0.10", {"alice": 33, "bob": 33, "carol": 34}),
    ("0.01", {"alice": 50, "bob": 50}),
    ("100.00", {"alice": 33, "bob": 33, "carol": 34}),
    ("12.50", {"alice": 50, "bob": 30, "carol": 20}),
    ("19.99", {"alice": 25, "bob": 25, "carol": 25, "dave": 25}),
    ("0.05", {"alice": 10, "bob": 10, "carol": 80}),
    ("7.77", {"alice": 1, "bob": 99}),
    ("0.03", {"alice": 100}),
]


@pytest.mark.parametrize(("amount", "percents"), SPLITS)
def test_percent_shares_add_up_to_the_amount(run, amount, percents):
    code, _, err = run(*ADD, "--amount", amount, *percent_options(percents))
    assert code == 0, err
    balances = balances_in_cents(run)
    total = cents_of(amount)
    shares = {name: -balances.get(name, 0) for name in percents}
    assert balances["zed"] == total
    assert sum(shares.values()) == total, f"shares {shares} do not add up to {total} cents"
    for name, pct in percents.items():
        exact = Fraction(total * pct, 100)
        assert math.floor(exact) <= shares[name] <= math.ceil(exact), f"{name} owes {shares[name]} of exactly {exact}"


def test_shares_of_several_percent_expenses_accumulate(run):
    run(*ADD, "--amount", "0.10", *percent_options({"alice": 33, "bob": 33, "carol": 34}))
    run(*ADD, "--amount", "0.10", *percent_options({"alice": 33, "bob": 33, "carol": 34}))
    balances = balances_in_cents(run)
    assert sum(balances.values()) == 0
    assert balances["zed"] == 20
    assert -balances["alice"] - balances["bob"] - balances["carol"] == 20


BAD_PERCENTS = [
    pytest.param(["alice=50", "bob=40"], id="adds-up-to-90"),
    pytest.param(["alice=60", "bob=50"], id="adds-up-to-110"),
    pytest.param(["alice=abc", "bob=100"], id="not-a-number"),
    pytest.param(["alice", "bob=100"], id="no-equals-sign"),
    pytest.param(["alice=-10", "bob=110"], id="negative"),
    pytest.param(["alice=50", "alice=50"], id="same-person-twice"),
]


@pytest.mark.parametrize("percents", BAD_PERCENTS)
def test_invalid_percentages_are_rejected_and_nothing_is_saved(run, percents):
    code, _, err = run(*ADD, "--amount", "9.00", *[o for p in percents for o in ("--percent", p)])
    assert code == 2
    assert "error" in err
    assert run("list")[1] == ""
    assert run("balances")[1] == ""


def test_equal_split_is_unchanged(run):
    code, out, _ = run(
        "add", "--paid-by", "alice", "--amount", "10.00", "--description", "Snacks",
        "--with", "alice", "--with", "bob", "--with", "carol",
    )  # fmt: skip
    assert code == 0
    assert out == "added #1: 10.00 for Snacks\n"
    assert run("balances")[1] == "alice 6.66\nbob -3.33\ncarol -3.33\n"


def test_equal_and_percent_expenses_can_be_mixed(run):
    run("add", "--paid-by", "alice", "--amount", "30.00", "--description", "Pizza",
        "--with", "alice", "--with", "bob", "--with", "carol")  # fmt: skip
    run(*ADD, "--amount", "12.50", *percent_options({"alice": 50, "bob": 30, "carol": 20}))
    balances = balances_in_cents(run)
    assert balances == {"alice": 2000 - 625, "bob": -1000 - 375, "carol": -1000 - 250, "zed": 1250}
