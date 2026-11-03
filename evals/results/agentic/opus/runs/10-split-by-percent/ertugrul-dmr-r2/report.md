`tabtally add` now takes `--percent NAME=PCT` as another way to split an expense. All 52 tests pass, and I also ran the command by hand to check it.

```console
$ python -m tabtally add --paid-by alice --amount 10.01 --description Dinner --percent alice=50 --percent bob=30 --percent carol=20
added #1: 10.01 for Dinner
$ python -m tabtally balances
alice 5.00
bob -3.00
carol -2.00
```

**How it behaves**
- You use either `--with` or `--percent`, not both. Using both, or neither, is a usage error (exit code 2).
- **Percentages:** each one must be a whole number. Values like `alice`, `alice=`, `=50`, `alice=12.5`, `alice=-10` and `alice=x` are rejected before anything is saved.
- If the percentages don't add up to 100, you get `error: percentages must add up to 100, not 90`. A name listed twice is also an error, the same as with `--with`.
- A 0% share is allowed. It's legal but means that person owes nothing, so say if you'd rather reject it.
- No cents are lost. Leftover cents go to the person whose exact share was rounded down the most. In the example above, alice owes 5.01 of the 10.01.

**Changes**
- `tabtally/splitting.py`: new `split_by_percent(cents, percents)`, which takes `(name, percent)` pairs so duplicate names can still be caught. It reuses the existing `allocate`. I moved the duplicate check into a shared `_reject_duplicates` helper so both split functions use the same code instead of each having its own copy (G5). The 100 is a named constant, `WHOLE` (G25).
- `tabtally/cli.py`: `--with` and `--percent` are now an argparse group where exactly one is required. A `_parse_percent` function checks the `NAME=PCT` format, so a badly formed value gets argparse's normal usage error.
- Tests: 18 new ones covering normal splits, leftover cents, a single person at 100%, 0%, totals of 99 and 101, negative and duplicate entries, malformed values, and using both or neither option.
- `README.md`: added the new form of `add` to the command table.

Nothing is committed yet.