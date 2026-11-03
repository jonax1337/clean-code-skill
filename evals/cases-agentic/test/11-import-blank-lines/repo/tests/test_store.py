from datetime import date

from hourlog import store
from hourlog.entries import Entry


def test_missing_file_means_no_entries(tmp_path):
    assert store.load(tmp_path / "nothing.json") == []


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "log.json"
    entries = [Entry(date(2025, 3, 3), "Acme", 90)]
    store.save(path, entries)
    assert store.load(path) == entries


def test_append_keeps_earlier_entries(tmp_path):
    path = tmp_path / "log.json"
    first, second = Entry(date(2025, 3, 3), "Acme", 90), Entry(date(2025, 3, 4), "Globex", 45)
    store.append(path, [first])
    store.append(path, [second])
    assert store.load(path) == [first, second]
