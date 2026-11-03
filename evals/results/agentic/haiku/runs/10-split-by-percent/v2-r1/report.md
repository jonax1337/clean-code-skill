`tabtally add` now accepts `--percent NAME=PCT`. The percentages must total 100, and the cents are split with the same largest-remainder rounding that `--with` uses, so the shares always add up to the amount. All 50 tests pass (34 existing, 16 new), and I ran the CLI end to end.

```
$ tabtally add --paid-by alice --amount 10.00 --description Snacks --percent alice=34 --percent bob=33 --percent carol=33
added #1: 10.00 for Snacks
$ tabtally balances
alice 6.60
bob -3.30
carol -3.30
```

Changes:
- **`tabtally/splitting.py`**: `parse_percent` turns `NAME=PCT` into a name and a whole number. `split_by_percent` checks for duplicate names and the total of 100, then calls the existing `allocate`. The duplicate check moved into a helper that `split_equally` also uses.
- **`tabtally/cli.py`**: `--with` and `--percent` are in a required mutually exclusive group, so exactly one of them must be given.
- **Tests**: new cases in `test_splitting.py` and `test_cli.py` cover the split, rounding, the total-of-100 rule, duplicates, bad input, and the mutual exclusion.
- **`README.md`**: a row for the new form in the commands table.

Choices I made that you may want to change:
- `--with` and `--percent` cannot be combined. Argparse rejects the mix with exit code 2.
- A percentage of `0` is accepted. Such a person stays in the expense with a zero share. Rejecting it is a one-line change.
- The percentage must be plain ASCII digits, so `+5`, `50.5` and `-5` are rejected.
- Whitespace around the name and the number is trimmed. Everything after the first `=` is treated as the percentage.

I have not committed anything.