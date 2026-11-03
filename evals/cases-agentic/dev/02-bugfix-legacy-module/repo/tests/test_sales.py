import datetime

from reports.sales import monthly_report, quarterly_report

ROWS = [
    {"date": datetime.date(2026, 2, 28), "amount_cents": 999},
    {"date": datetime.date(2026, 3, 1), "amount_cents": 1500},
    {"date": datetime.date(2026, 3, 31), "amount_cents": 2500},
    {"date": datetime.date(2026, 4, 1), "amount_cents": 700},
]


def test_monthly_report_counts_only_the_month():
    assert monthly_report(ROWS, 2026, 3) == {"period": "2026-03", "orders": 2, "total_cents": 4000}


def test_quarterly_report_counts_only_the_quarter():
    assert quarterly_report(ROWS, 2026, 1) == {"period": "2026-Q1", "orders": 3, "total_cents": 4999}
