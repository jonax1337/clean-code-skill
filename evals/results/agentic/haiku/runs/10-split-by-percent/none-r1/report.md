`tabtally add` now takes `--percent NAME=PCT`, which splits an expense by whole-number percentages. All 51 tests pass (34 existing, 17 new).

Example run:

```
$ python -m tabtally add --paid-by alice --amount 30.00 --description Dinner --percent alice=50 --percent bob=30 --percent carol=20
added #1: 30.00 for Dinner
```

Behaviour and choices I made:

- **`--with` and `--percent` are mutually exclusive, and one of them is required.** Giving both, or neither, is a usage error (exit code 2), the same code as other bad input.
- **Percentages must be whole numbers and sum to exactly 100.** Anything else, such as `50.5`, `+5`, `-5`, a missing `=`, or a sum of 90 or 110, is rejected and nothing is saved.
- **Cents are split with the existing `allocate` helper,** so leftover cents go to the largest remainders and the shares always add up to the amount. For example, 10.00 split 34/33/33 gives 3.40, 3.30, 3.30.
- **Duplicate names are rejected,** as they already are for `--with`. I moved that check into a shared helper in `splitting.py`.
- **A 0% share is allowed,** since 0 is a whole number. Say if you'd rather reject it.
- **The name is split from the percentage at the last `=`.** A name that itself contains `=` therefore still works.

The changes are in `tabtally/splitting.py`, `tabtally/cli.py`, the two test files, and a new row in the README's command table. I haven't committed anything.