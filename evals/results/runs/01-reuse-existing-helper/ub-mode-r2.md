I couldn't run anything in this session, so neither the test nor the change has been executed.

## 1. Failing test first

`tests/test_invoice.py` (new file, or append if you already have one):

```python
from decimal import Decimal
from types import SimpleNamespace

from billing.invoice import format_invoice_total


def item(price, qty):
    return SimpleNamespace(price=Decimal(price), qty=qty)


def test_footer_total_uses_german_separators_and_includes_vat():
    items = [item("500.00", 1), item("250.00", 2)]  # net 1000.00, gross 1190.00
    assert format_invoice_total(items) == "1.190,00 EUR"


def test_footer_total_rounds_half_up_on_the_gross_amount():
    items = [item("10.005", 1)]  # gross 11.90595
    assert format_invoice_total(items) == "11,91 EUR"
```

Expected failure right now: `ImportError: cannot import name 'format_invoice_total'`.

## 2. The change to `billing/invoice.py`

Append at the end:

```python
def format_invoice_total(items, currency: str = "EUR") -> str:
    return format_currency(invoice_total(items), currency)
```

This is the whole edit. It reuses `invoice_total` for the amount and `format_currency` for the formatting, so neither decision is duplicated. Rounding happens only once, at display time, on the gross amount.

## Log

- Read `invoice.py`. `invoice_total` and `format_currency` already cover the calculation and the formatting, so I only needed to compose them.
- Wrote two behavior tests that call the public function the way the PDF footer would. One covers the separators and VAT, the other covers half-up rounding.
- Added a three-line function that composes the two existing ones. I added no new logic and changed nothing else.

## Not done

- I didn't run the tests, so please run them and confirm the first one fails before the edit and both pass after.
- I didn't run the crapper, dryer or mutator tools, since I don't have them here. The new function has no branches, so it shouldn't matter for CRAP.
- There is no git repository in this directory, so I made no commit or push.