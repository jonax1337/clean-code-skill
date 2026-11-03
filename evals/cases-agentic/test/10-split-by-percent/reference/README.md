# tabtally

Keep track of shared expenses in a small JSON file and see who owes whom.

```console
$ python -m tabtally add --paid-by alice --amount 30.00 --description Pizza --with alice --with bob --with carol
added #1: 30.00 for Pizza
$ python -m tabtally balances
alice 20.00
bob -10.00
carol -10.00
```

## Commands

All commands accept `--file PATH` before the command name (default `tabtally.json`).

| Command | What it does |
| --- | --- |
| `add --paid-by NAME --amount AMOUNT --description TEXT --with NAME ...` | Record an expense that the named people share equally. Repeat `--with` for each person. |
| `add --paid-by NAME --amount AMOUNT --description TEXT --percent NAME=PERCENT ...` | Record an expense that is split by whole percentages instead. Repeat `--percent` for each person; the percentages must add up to 100. Use either `--with` or `--percent`, not both. |
| `list` | Print every recorded expense. |
| `balances` | Print what each person is owed (positive) or owes (negative). |

Amounts are written like `12.50`, with at most two decimals. Internally every amount is a whole number of cents, so shares always add up to the amount that was paid.

## Development

```console
python -m pytest
```
