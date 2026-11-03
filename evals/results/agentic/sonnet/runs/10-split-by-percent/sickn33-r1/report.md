`tabtally add` now takes `--percent NAME=PCT`, repeated once per person, and the full suite passes (49 tests).

- **Parsing:** `parse_percent` in `tabtally/splitting.py` accepts only whole numbers, so `alice=12.5`, `alice=-5`, `alice=` and `=50` are rejected.
- **Splitting:** `split_by_percent` in the same file requires the percentages to add up to exactly 100. It also rejects a person listed twice and a 0% share. It reuses `allocate`, so the shares always add up to the amount to the cent. For example, 10.01 split 33/33/34 loses nothing.
- **CLI:** `--with` is no longer required by argparse. Instead, `add` must get either `--with` or `--percent`, and giving both or neither is an error. It prints `error: …` and exits with code 2, like the other validation errors, and nothing is saved.
- **Tests and docs:** I added tests for the splitting functions and the CLI cases, and a README table row for the new option.

I didn't commit anything.