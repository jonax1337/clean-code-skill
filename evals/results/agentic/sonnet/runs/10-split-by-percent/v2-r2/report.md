`tabtally add` now accepts `--percent NAME=PCT`, and the full test suite passes (49 tests). I haven't committed anything.

With your example, `--percent alice=50 --percent bob=30 --percent carol=20` splits a 10.00 expense into 5.00, 3.00 and 2.00. Leftover cents are handed out by the existing `allocate` function, the same way the equal split does it.

- **`--with` vs `--percent`:** `add` needs exactly one of them. Using both, or neither, is a usage error.
- **Percentages:** they must be whole numbers from 1 to 100 and add up to 100. Malformed entries (`alice`, `alice=`, `alice=5.5`, `alice=0`) are rejected. So is a name listed twice. Errors print as `error: …` with exit code 2, and nothing is saved.
- **0%:** I chose to reject `alice=0` because a person with no share has no reason to be listed. Say if you want it allowed.
- **Code:** the new `split_by_percent` is in `tabtally/splitting.py` and reuses the duplicate-name check from the equal split. The option itself is in `tabtally/cli.py`.
- **Tests and docs:** I added tests for the splitting, the CLI behaviour and the error cases, and a `--percent` row in the README command table.