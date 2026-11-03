import datetime

from reports.periods import month_range, quarter_range, week_range


def test_month_range_is_half_open():
    assert month_range(2026, 3) == (datetime.date(2026, 3, 1), datetime.date(2026, 4, 1))


def test_quarter_range_is_half_open():
    assert quarter_range(2026, 2) == (datetime.date(2026, 4, 1), datetime.date(2026, 7, 1))


def test_week_range_starts_on_monday():
    assert week_range(datetime.date(2026, 11, 5)) == (datetime.date(2026, 11, 2), datetime.date(2026, 11, 9))
