import pytest

from tabtally.errors import MoneyError
from tabtally.splitting import split_equally


def test_split_equally_gives_everyone_the_same_share():
    assert split_equally(900, ["alice", "bob", "carol"]) == {"alice": 300, "bob": 300, "carol": 300}


def test_split_equally_keeps_every_cent():
    shares = split_equally(1000, ["alice", "bob", "carol"])
    assert sum(shares.values()) == 1000
    assert sorted(shares.values()) == [333, 333, 334]


def test_split_equally_rejects_a_person_listed_twice():
    with pytest.raises(MoneyError, match="bob"):
        split_equally(1000, ["bob", "alice", "bob"])
