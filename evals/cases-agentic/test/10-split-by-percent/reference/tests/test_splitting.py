import pytest

from tabtally.errors import MoneyError
from tabtally.splitting import split_by_percent, split_equally


def test_split_equally_gives_everyone_the_same_share():
    assert split_equally(900, ["alice", "bob", "carol"]) == {"alice": 300, "bob": 300, "carol": 300}


def test_split_equally_keeps_every_cent():
    shares = split_equally(1000, ["alice", "bob", "carol"])
    assert sum(shares.values()) == 1000
    assert sorted(shares.values()) == [333, 333, 334]


def test_split_equally_rejects_a_person_listed_twice():
    with pytest.raises(MoneyError, match="bob"):
        split_equally(1000, ["bob", "alice", "bob"])


def test_split_by_percent_follows_the_percentages():
    assert split_by_percent(1000, {"alice": 50, "bob": 30, "carol": 20}) == {"alice": 500, "bob": 300, "carol": 200}


def test_split_by_percent_keeps_every_cent():
    shares = split_by_percent(10, {"alice": 33, "bob": 33, "carol": 34})
    assert sum(shares.values()) == 10


def test_split_by_percent_rejects_percentages_that_do_not_add_up():
    with pytest.raises(MoneyError, match="100"):
        split_by_percent(1000, {"alice": 60, "bob": 50})
