"""Date ranges for the sales reports. Every range is half-open: start <= day < end."""

import datetime


def month_range(year, month):
    """Return (first day of the month, first day of the next month)."""
    start = datetime.date(year, month, 1)
    end = _first_day_after_months(year, month, 1)
    return start, end


def quarter_range(year, quarter):
    """Return (first day of the quarter, first day of the next quarter) for quarter 1-4."""
    start = datetime.date(year, 3 * quarter - 2, 1)
    end = _first_day_after_months(year, 3 * quarter, 1)
    return start, end


def week_range(day):
    """Return (Monday of the ISO week containing day, Monday of the following week)."""
    start = day - datetime.timedelta(days=day.weekday())
    return start, start + datetime.timedelta(days=7)


def _first_day_after_months(year, month, months):
    """First day of the month that comes `months` months after the given month."""
    index = year * 12 + (month - 1) + months
    return datetime.date(index // 12, index % 12 + 1, 1)
