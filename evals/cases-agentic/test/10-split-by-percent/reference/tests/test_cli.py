import pytest

from tabtally.cli import main


@pytest.fixture
def run(tmp_path, capsys):
    def invoke(*argv):
        code = main(["--file", str(tmp_path / "tabtally.json"), *argv])
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return invoke


def test_add_records_an_equal_split(run):
    code, out, _ = run(
        "add", "--paid-by", "alice", "--amount", "30.00", "--description", "Pizza",
        "--with", "alice", "--with", "bob", "--with", "carol",
    )  # fmt: skip
    assert code == 0
    assert out == "added #1: 30.00 for Pizza\n"


def test_list_shows_every_expense(run):
    run("add", "--paid-by", "alice", "--amount", "5", "--description", "Coffee", "--with", "bob")
    run("add", "--paid-by", "bob", "--amount", "7.50", "--description", "Lunch", "--with", "alice")
    _, out, _ = run("list")
    assert out == "#1 alice paid 5.00 for Coffee\n#2 bob paid 7.50 for Lunch\n"


def test_balances_show_who_owes_whom(run):
    run(
        "add", "--paid-by", "alice", "--amount", "30.00", "--description", "Pizza",
        "--with", "alice", "--with", "bob", "--with", "carol",
    )  # fmt: skip
    _, out, _ = run("balances")
    assert out == "alice 20.00\nbob -10.00\ncarol -10.00\n"


def test_odd_cents_are_not_lost(run):
    run(
        "add", "--paid-by", "alice", "--amount", "10.00", "--description", "Snacks",
        "--with", "alice", "--with", "bob", "--with", "carol",
    )  # fmt: skip
    _, out, _ = run("balances")
    assert out == "alice 6.66\nbob -3.33\ncarol -3.33\n"


def test_bad_amount_is_reported_and_nothing_is_saved(run):
    code, _, err = run("add", "--paid-by", "alice", "--amount", "abc", "--description", "x", "--with", "bob")
    assert code == 2
    assert err.startswith("error:")
    assert run("list")[1] == ""


def test_person_listed_twice_is_rejected(run):
    code, _, err = run(
        "add", "--paid-by", "alice", "--amount", "9", "--description", "x", "--with", "bob", "--with", "bob"
    )
    assert code == 2
    assert "bob" in err
    assert run("list")[1] == ""


def test_percent_split_is_applied(run):
    code, _, _ = run(
        "add", "--paid-by", "dana", "--amount", "12.50", "--description", "Dinner",
        "--percent", "alice=50", "--percent", "bob=30", "--percent", "carol=20",
    )  # fmt: skip
    assert code == 0
    _, out, _ = run("balances")
    assert out == "alice -6.25\nbob -3.75\ncarol -2.50\ndana 12.50\n"


def test_percent_split_does_not_lose_cents(run):
    run(
        "add", "--paid-by", "dana", "--amount", "0.10", "--description", "Gum",
        "--percent", "alice=33", "--percent", "bob=33", "--percent", "carol=34",
    )  # fmt: skip
    _, out, _ = run("balances")
    assert out == "alice -0.03\nbob -0.03\ncarol -0.04\ndana 0.10\n"


@pytest.mark.parametrize(
    "percents",
    [["alice=50", "bob=40"], ["alice=60", "bob=50"], ["alice=x", "bob=100"], ["alice", "bob=100"], ["alice=50", "alice=50"]],
)
def test_bad_percentages_are_rejected_and_nothing_is_saved(run, percents):
    argv = ["add", "--paid-by", "dana", "--amount", "9", "--description", "x"]
    for percent in percents:
        argv += ["--percent", percent]
    code, _, err = run(*argv)
    assert code == 2
    assert "error" in err
    assert run("list")[1] == ""
