`tabtally add` now takes `--percent NAME=PCT`, e.g. `--percent alice=50 --percent bob=30 --percent carol=20`. All 49 tests pass, including the new ones.

**What changed**
- **`tabtally/cli.py`:** `--with` and `--percent` are now alternatives, and you must give exactly one. Using both, or neither, gets argparse's usage error (exit code 2). Each `NAME=PCT` is checked and turned into a name and a number.
- **`tabtally/splitting.py`:** new `split_by_percent`. It rejects names listed twice and percentages that don't add up to 100, then uses the existing `allocate` to divide the cents, so the shares always add up to the full amount. The duplicate-name check moved into a helper that both split functions share; `split_equally` behaves exactly as before.
- **README:** documents the new form of `add`.

**One rule I chose:** a percentage must be a whole number from 1 up, so `bob=0`, `bob=-10`, `bob=50.5`, `bob=` and `bob` are all rejected with an `error:` message, and nothing is saved. A 0% share didn't seem useful, but allowing it is a one-line change if you want it.

**Tests:** added tests for a percentage split, a split with an odd cent left over, totals other than 100, a name listed twice, badly formed `--percent` values, and combining `--with` with `--percent`. I ran `python -m pytest`: 49 passed. There's no linter or formatter set up in `pyproject.toml`, and `ruff` isn't installed here, so neither was run.

Nothing is committed.