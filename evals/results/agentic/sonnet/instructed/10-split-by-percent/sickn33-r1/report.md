`tabtally add` now takes `--percent NAME=PCT`, repeated once per person, as an alternative to `--with`. All 47 tests pass, including the new ones.

- **Option rules:** `--with` and `--percent` can't be used together, and one of them is required. Mixing them gets argparse's usual usage error.
- **Validation:** Percentages must be whole, non-negative numbers (`alice=5.5`, `alice=-5` and `=50` are rejected). They must add up to exactly 100, or you get `error: percentages must add up to 100, got N` with exit code 2. Nothing is saved on error. Listing a person twice is rejected, same as with `--with`.
- **Rounding:** The split reuses the existing `allocate` function, so a share that doesn't divide evenly gets its leftover cents from the largest remainders. The shares always sum to the exact amount.
- **Code changes:** The new functions are in `tabtally/splitting.py` and the option wiring is in `tabtally/cli.py`. The tests are in `tests/test_splitting.py` and `tests/test_cli.py`.

I didn't update the README, and I haven't checked whether it documents `--with`.