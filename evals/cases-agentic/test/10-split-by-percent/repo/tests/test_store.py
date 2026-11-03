import pytest

from tabtally import store
from tabtally.errors import StoreError
from tabtally.models import Expense


def test_missing_file_is_an_empty_list(tmp_path):
    assert store.load(tmp_path / "nothing.json") == []


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "t.json"
    expenses = [Expense(1, "alice", "Pizza", 3000, {"alice": 1500, "bob": 1500})]
    store.save(path, expenses)
    assert store.load(path) == expenses


def test_broken_file_is_reported(tmp_path):
    path = tmp_path / "t.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(StoreError):
        store.load(path)


def test_next_id_follows_the_highest_id():
    expenses = [Expense(4, "a", "x", 100, {"a": 100}), Expense(2, "a", "y", 100, {"a": 100})]
    assert store.next_id(expenses) == 5
    assert store.next_id([]) == 1
