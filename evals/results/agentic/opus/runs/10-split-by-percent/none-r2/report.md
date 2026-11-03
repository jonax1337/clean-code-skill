`tabtally add` now accepts `--percent NAME=PCT`, so an expense can be split by percentage. All 53 tests pass (34 existing, 19 new), and I tried it by hand: a 10.00 taxi split 33/33/34 gives alice 6.70, bob -3.30, carol -3.40.

**How it works**
- `--with` and `--percent` are alternatives: you must give one of them, and giving both is an error.
- The split reuses the existing `allocate` function, so shares always add up to the exact amount. When a cent can't be divided evenly, it goes to the person who would lose the most to rounding, and to the person listed first on a tie. For example, 0.01 split 50/50 gives alice 0.01 and bob 0.00.

**What gets rejected** (exit code 2, and nothing is saved)
- Percentages that don't add up to exactly 100.
- The same person listed twice.
- Values that aren't in the form `NAME=PCT` with a plain whole number, such as `bob`, `alice=12.5`, `alice=-5` or `alice=+5`.
- Percentages outside 1–100. **I chose to reject 0%**, since a person with a zero share has no reason to be on the expense. If you'd rather allow it, it's a one-line change in `parse_percent`.

**Changes**
- `tabtally/splitting.py`: new `parse_percent` and `split_by_percent`. I moved the duplicate-name check into a shared helper.
- `tabtally/cli.py`: the new option and how `add` picks which split to use.
- `README.md`: documents the new form of `add`.
- `tests/test_splitting.py` and `tests/test_cli.py`: tests for the new behaviour.

Nothing is committed yet.