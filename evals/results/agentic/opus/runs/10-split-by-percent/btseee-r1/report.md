`tabtally add` now accepts `--percent NAME=PCT`. All 49 tests pass: the 34 that were already there plus 15 new ones.

```console
$ python -m tabtally add --paid-by alice --amount 100 --description Groceries \
    --percent alice=50 --percent bob=30 --percent carol=20
added #1: 100.00 for Groceries
$ python -m tabtally balances
alice 50.00
bob -30.00
carol -20.00
```

**What changed**
- **`tabtally/splitting.py`**: a new `split_by_percent` function does the split. It reuses the existing cent-splitting code, so the shares always add up to exactly the amount paid; for example, 10.01 split 50/30/20 doesn't lose the extra cent. The check for a person listed twice is now shared between the equal split and the percentage split.
- **`tabtally/cli.py`**: you use either `--with` or `--percent` on a given expense, not both, and one of them is required. The `NAME=PCT` text is checked as it's read, and anything that isn't a whole number, like `bob=12.5`, `bob=-5` or `bob=`, gets the standard usage message.
- **Tests** cover exact splits, odd cents, totals other than 100, a 0% share, a person listed twice, badly formed `--percent` values, and using `--with` and `--percent` together.
- **`README.md`**: the commands table has a row for `--percent`.

**How errors show up**
- If the percentages don't add up to 100, or the same person is listed twice, you get an `error: ...` line, exit code 2, and nothing is saved. That's the same handling as the existing "person listed twice" error.
- Badly formed `NAME=PCT` text, or using `--with` and `--percent` together, gets argparse's usage message. That also exits with code 2.

**One decision for you:** a 0% share like `bob=0` is rejected, because it would just add a person who owes nothing. If you'd rather allow it, delete the range check in `split_by_percent`; the cent splitting already handles a zero.

Nothing is committed.