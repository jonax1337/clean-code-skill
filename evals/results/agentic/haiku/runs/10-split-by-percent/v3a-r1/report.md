`tabtally add` now takes `--percent NAME=PCT` as an alternative to `--with`. The full suite passes (50 tests, up from 34).

```
python -m tabtally add --paid-by alice --amount 30.00 --description Pizza --percent alice=50 --percent bob=30 --percent carol=20
python -m tabtally balances
alice 15.00
bob -9.00
carol -6.00
```

**Behavior**
- `--with` and `--percent` are mutually exclusive, and one of them is required. Mixing them is a usage error (exit code 2).
- Each value must look like `NAME=PCT`. `PCT` must be a whole number from 1 to 100. Anything else, like `12.5`, `-5`, `0`, or a missing name, is rejected.
- The percentages must add up to 100. Otherwise nothing is saved and the error names the total, e.g. `percentages must add up to 100, not 90`.
- A name listed twice is rejected, same as with `--with`.
- Cents are split with the existing `allocate` helper, so the shares always add up to the exact amount.

**Choices I made that you may want to change**
- I chose to reject `0%`. A zero share would be legal in the math, but it's more likely a typo. Allowing it is a one-line change.
- `--percent` replaces `--with` rather than adding to it. Someone can't mix equal and percentage shares in one expense.

**Files changed**
- `tabtally/splitting.py`: added `parse_percent` and `split_by_percent`. I moved the duplicate-name check into a shared `_reject_duplicates` helper.
- `tabtally/cli.py`: `add` now has a mutually exclusive group for `--with` and `--percent`.
- `tests/test_splitting.py` and `tests/test_cli.py`: new tests for parsing, the exact split, the sum-to-100 check, duplicates, and the flag conflict.
- `README.md`: documented the new form of `add`.

I did not commit anything.