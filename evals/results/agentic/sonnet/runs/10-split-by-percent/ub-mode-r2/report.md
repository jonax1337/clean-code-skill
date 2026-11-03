`tabtally add` now takes `--percent NAME=PCT`, and the full test suite passes (47 tests). The commit is on `main` but not pushed, because the repo has no remote.

**Behavior:**
- **Splitting:** `--percent alice=50 --percent bob=30 --percent carol=20` splits the amount by those percentages. It reuses the existing cent-splitting code, so no cent is lost.
- **Mutually exclusive with `--with`:** `--with` and `--percent` can't be combined, and one of them is required.
- **Validation:** an entry that isn't `NAME=PCT`, a percentage that isn't a whole number, a name listed twice, or percentages that don't add up to 100 are rejected with `error: …` and exit code 2. Nothing is saved in those cases.

**Where the changes are:**
- **Code:** the new `split_by_percent` and its parsing are in `tabtally/splitting.py`, and the option is wired up in `tabtally/cli.py`.
- **Tests and README:** I added unit and CLI tests, and a README row for the new option.

**Log:**
1. Read the CLI, splitting and money code.
2. Wrote failing tests and confirmed they failed on the missing `split_by_percent`.
3. Implemented `split_by_percent` and the CLI option.
4. Updated the README.
5. Committed.
6. Tried to push and found no remote.

I didn't run the crapper, dryer or mutator tools, because I didn't find them in the repo.