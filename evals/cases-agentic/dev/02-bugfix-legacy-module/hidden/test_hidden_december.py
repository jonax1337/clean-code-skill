import datetime

from reports.periods import month_range
from reports.sales import monthly_report


def test_every_month_ends_where_the_next_one_begins():
    for month in range(1, 13):
        next_start = datetime.date(2027, 1, 1) if month == 12 else datetime.date(2026, month + 1, 1)
        assert month_range(2026, month) == (datetime.date(2026, month, 1), next_start)


def test_december_report_includes_new_years_eve_and_nothing_after():
    rows = [
        {"date": datetime.date(2026, 11, 30), "amount_cents": 7},
        {"date": datetime.date(2026, 12, 31), "amount_cents": 1000},
        {"date": datetime.date(2027, 1, 1), "amount_cents": 5},
    ]
    assert monthly_report(rows, 2026, 12) == {"period": "2026-12", "orders": 1, "total_cents": 1000}
