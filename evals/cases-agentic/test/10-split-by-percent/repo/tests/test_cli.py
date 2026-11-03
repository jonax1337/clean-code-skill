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
