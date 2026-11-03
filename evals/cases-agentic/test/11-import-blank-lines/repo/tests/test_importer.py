from datetime import date

import pytest

from hourlog.entries import Entry
from hourlog.importer import ImportFormatError, parse_entries


def test_parses_one_entry_per_line():
    lines = ["2025-03-03,Acme,90\n", "2025-03-04,Globex,45\n"]
    assert parse_entries(lines) == [
        Entry(date(2025, 3, 3), "Acme", 90),
        Entry(date(2025, 3, 4), "Globex", 45),
    ]


def test_accepts_windows_line_endings_and_spaces_around_fields():
    assert parse_entries(["2025-03-03 , Acme ,90\r\n"]) == [Entry(date(2025, 3, 3), "Acme", 90)]


def test_the_last_line_needs_no_newline():
    assert parse_entries(["2025-03-03,Acme,90"]) == [Entry(date(2025, 3, 3), "Acme", 90)]


def test_no_lines_give_no_entries():
    assert parse_entries([]) == []


def test_bad_date_names_the_line():
    with pytest.raises(ImportFormatError, match=r"line 2\b"):
        parse_entries(["2025-03-03,Acme,90\n", "03/04/2025,Acme,45\n"])


def test_bad_minutes_name_the_line():
    with pytest.raises(ImportFormatError, match=r"line 1\b"):
        parse_entries(["2025-03-03,Acme,lots\n"])


def test_zero_minutes_are_rejected():
    with pytest.raises(ImportFormatError, match="positive"):
        parse_entries(["2025-03-03,Acme,0\n"])
