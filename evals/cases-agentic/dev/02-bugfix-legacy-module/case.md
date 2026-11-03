# Bugfix in a legacy module with a sibling bug (Python)

Tests: root-cause fix instead of a special case, a regression test that fails without the fix, no drive-by cleanup of the messy code around it, the sibling bug with the same root cause is fixed or at least reported (T6), verified by running the tests.

## Prompt

The December sales report crashes:

```
>>> monthly_report(rows, 2026, 12)
Traceback (most recent call last):
  ...
ValueError: month must be in 1..12
```

Can you fix it?
