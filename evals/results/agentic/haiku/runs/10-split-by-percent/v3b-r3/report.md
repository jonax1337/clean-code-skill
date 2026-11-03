`tabtally add` now accepts `--percent NAME=PCT`, repeated per person. The example from your request works: a $30.00 pizza splits to alice 15.00, bob 9.00, carol 6.00. All 50 tests pass (34 existing, 16 new).

**Changes**
- `tabtally/splitting.py`: new `split_by_percent`. It rejects percentages that don't sum to 100 and reuses `allocate`, so cents are never lost. The duplicate-name check moved into a helper that both split functions use.
- `tabtally/cli.py`: `--with` and `--percent` are now a required mutually exclusive group, so an expense uses one or the other. `NAME=PCT` parsing rejects a missing name or `=`, non-integers, negatives, and anything outside 1–100.
- `tests/`: unit tests for the split, and CLI tests for the happy path, the sum check, malformed entries, and the `--with`/`--percent` conflict.
- `README.md`: a row for the new form in the command table.

**Choices I made that you may want to change**
- `--percent` replaces `--with` rather than adding to it. Mixing equal and percentage shares in one expense would have needed rules for how they combine.
- A 0% share is rejected. It is valid arithmetic, but it's almost always a typo.
- The name is everything before the first `=`.

Nothing is committed.