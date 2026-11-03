`tabtally add` now accepts `--percent NAME=PCT`, repeated once per person, as an alternative to `--with`. All tests pass (52, up from 34 before the change).

```console
$ python -m tabtally add --paid-by alice --amount 30.00 --description Pizza \
    --percent alice=50 --percent bob=30 --percent carol=20
added #1: 30.00 for Pizza
$ python -m tabtally balances
alice 15.00
bob -9.00
carol -6.00
```

**What changed**
- **`tabtally/splitting.py`**:
  - `split_by_percentage(cents, [(name, pct), ...])` uses the existing `allocate`, so the shares always add up to the full amount. Leftover cents go to the largest remainders, as with equal splits: 10.01 split 50/30/20 gives 5.01, 3.00 and 2.00.
  - `parse_percentage("alice=50")` turns the text into a name and a number.
  - I moved the duplicate-name check into a shared helper so both split types use it.
- **`tabtally/cli.py`**: `--with` and `--percent` are now alternatives: you must give one, and giving both is an error.
- **`README.md`**: documents the new form of `add`.

**What gets rejected** (exit code 2, nothing saved):
- percentages that don't add up to 100 (the message gives the actual total)
- a person listed twice
- a percentage of 0
- anything that isn't `NAME=<whole number>`, such as `alice=12.5`, `alice=-5`, `alice=+5` or `=50`

**Decision for you:** I rejected 0% because a 0% person owes nothing, so you can just leave them out. If you'd rather allow it, it's a one-line change.

**Tests:** I wrote them before the code. In `tests/test_splitting.py` they cover the exact split, the leftover cent, totals of 99 and 101, 0%, duplicates and bad input. In `tests/test_cli.py` they cover a full add followed by balances, a total that's wrong, and using `--with` and `--percent` together.