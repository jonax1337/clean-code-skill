`tabtally add` now takes `--percent NAME=PCT`, and all 52 tests pass. I also ran it by hand: `--amount 10.01 --percent alice=50 --percent bob=30 --percent carol=20` gives shares of 5.01 / 3.00 / 2.00. The odd cent goes to whoever has the largest remainder, which is how equal splits already work, so the shares still add up exactly.

**How it behaves**
- `--with` and `--percent` can't be used together, and `add` needs one of them.
- Each percentage must be a whole number, and the total must be exactly 100.
- Input like `alice=12.5`, `alice=fifty`, `=50`, or the same person listed twice gets an `error: ...` message and exit code 2, and nothing is saved.
- I also rejected 0%, which you didn't ask for: each percentage must be 1–100. A 0% entry is probably a typo, and the person would owe nothing anyway. If you want 0% allowed, it's a one-line change in `_reject_out_of_range`.

**Changes**
- `tabtally/splitting.py`: new `parse_percent` and `split_by_percent`, which use the existing `allocate` for the cent-exact maths. I moved the duplicate-name check into a helper so both split types use it.
- `tabtally/cli.py`: adds the `--percent` option and a small `_split` function that picks the split type.
- `README.md`: documents the new form of `add`.
- `tests/test_splitting.py` and `tests/test_cli.py`: new tests for the split maths, input parsing, the checks, and the CLI end to end. I wrote them before the code and confirmed they failed first.

I haven't committed anything.