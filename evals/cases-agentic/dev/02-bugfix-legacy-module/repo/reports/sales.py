from reports.periods import month_range, quarter_range


def sum_in_range(rows, start, end):
    t = 0
    for r in rows:
        if r["date"] >= start and r["date"] < end:
            t = t + r["amount_cents"]
    return t


def monthly_report(rows, year, month):
    start, end = month_range(year, month)
    total = sum_in_range(rows, start, end)
    cnt = len([r for r in rows if r["date"] >= start and r["date"] < end])
    return {"period": "%04d-%02d" % (year, month), "orders": cnt, "total_cents": total}


def quarterly_report(rows, year, quarter):
    start, end = quarter_range(year, quarter)
    total = sum_in_range(rows, start, end)
    cnt = len([r for r in rows if r["date"] >= start and r["date"] < end])
    return {"period": "%04d-Q%d" % (year, quarter), "orders": cnt, "total_cents": total}
