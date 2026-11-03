`tabtally add` now accepts `--percent NAME=PCT`, and the full suite passes (48 tests, up from 34). Changes are uncommitted in the working tree.

Your example works as expected: `add --paid-by alice --amount 10.00 ... --percent alice=50 --percent bob=30 --percent carol=20` records alice 5.00, bob 3.00 and carol 2.00 owed.

**Behavior:**
- `--percent` is repeatable and must be used instead of `--with`, not together with it. One of the two is required.
- Each value must be `NAME=PCT` with a non-negative whole number. Decimals, negatives, empty names, and a missing `=` are rejected with exit code 2.
- The percentages must add up to exactly 100. Otherwise the command fails and nothing is saved.
- Repeating a name is rejected, as it already is for `--with`.
- Cents are split with the existing `allocate` function, so uneven amounts still add up exactly.

**Choices I made that you may want to change:**
- A `0` percentage is allowed. That person gets a zero share. If you'd rather reject it, it's a one-line check in `split_by_percent`.
- Malformed `--percent` values go through argparse, so they exit 2 with a usage message. Sum and duplicate errors use the same `error:` path as other amount errors.

**Files:**
- `tabtally/splitting.py`: new `split_by_percent`. The duplicate check moved into a shared helper that both splits use.
- `tabtally/cli.py`: the `--with`/`--percent` mutually exclusive group, plus the `_percent` parser.
- `tests/test_splitting.py` and `tests/test_cli.py`: new tests for the sum rule, duplicates, malformed values, and the `--with`/`--percent` conflict.
- `README.md`: a row in the commands table.