`tabtally add` now accepts `--percent NAME=PCT`, and the shares are split by those percentages. The suite passes: 50 tests, up from 34. I did not commit.

```
$ tabtally add --paid-by alice --amount 100.00 --description Dinner --percent alice=50 --percent bob=30 --percent carol=20
added #1: 100.00 for Dinner
$ tabtally balances
alice 50.00
bob -30.00
carol -20.00
```

Changes:
- **`cli.py`**: `--with` and `--percent` are now a required mutually exclusive pair, so an `add` needs exactly one of them. The old `--with` requirement is covered by that group. A percent split is used when `--percent` is given.
- **`splitting.py`**: added `parse_percent` (accepts `NAME=PCT` with a whole number, and rejects things like `50.5`, `-5`, `50%`, or a missing name) and `split_by_percent`. The second rejects totals other than 100 and duplicate names. The duplicate check moved into a shared helper that `split_equally` also uses. Rounding goes through the existing `allocate`, so cents still add up exactly.
- **Tests**: unit tests for the new functions and CLI tests for the happy path, a bad total (nothing saved, exit 2), combining `--with` with `--percent`, and having neither option.
- **`README.md`**: a row for the new form in the command table.

Choices I made that you may want to change:
- A percentage of `0` is accepted, since the total still has to be 100.
- A person may not appear twice in `--percent`, matching the rule for `--with`.
- The payer is not added to the split automatically, same as `--with`.