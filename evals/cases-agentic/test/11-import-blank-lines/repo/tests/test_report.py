from datetime import date

import pytest

from hourlog.entries import Entry
from hourlog.report import format_duration, totals_by_project


def test_totals_add_up_per_project():
    entries = [
        Entry(date(2025, 3, 3), "Acme", 90),
        Entry(date(2025, 3, 4), "Globex", 45),
        Entry(date(2025, 3, 5), "Acme", 30),
    ]
    assert totals_by_project(entries) == {"Acme": 120, "Globex": 45}


@pytest.mark.parametrize(("minutes", "text"), [(0, "0h00"), (5, "0h05"), (90, "1h30"), (600, "10h00")])
def test_format_duration(minutes, text):
    assert format_duration(minutes) == text
