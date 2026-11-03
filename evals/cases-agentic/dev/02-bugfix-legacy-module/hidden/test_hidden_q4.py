import datetime

from reports.periods import quarter_range


def test_fourth_quarter_ends_at_new_year():
    assert quarter_range(2026, 4) == (datetime.date(2026, 10, 1), datetime.date(2027, 1, 1))
