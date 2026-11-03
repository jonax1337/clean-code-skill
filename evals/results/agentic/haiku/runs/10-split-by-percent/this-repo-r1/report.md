`tabtally add` now accepts `--percent NAME=PCT`, and the suite passes: 45 tests, up from 34, with 11 new ones covering the percentage path.

Behavior:
- `--percent alice=50 --percent bob=30 --percent carol=20` splits the amount in proportion, using the existing `allocate` helper, so the shares always add up to the full amount in cents.
- The percentages must be whole numbers and add up to exactly 100. Otherwise the command exits with code 2 and saves nothing, the same as the existing amount errors.
- `--with` and `--percent` are mutually exclusive and one of them is required. Passing neither or both is an argparse usage error.

Choices I made that you may want to change:
- **Zero and negative percentages are rejected.** A person at 0% is treated as a mistake, since they should just be left off the list.
- **Duplicate names are rejected** with the same message `--with` already uses.
- **Refactor:** the duplicate check moved into a shared `_reject_duplicates` helper in `tabtally/splitting.py`, used by both split functions.
- **README:** I added a row for the new form to the commands table.

I haven't committed anything. The changes are in `tabtally/cli.py`, `tabtally/splitting.py`, `tests/test_cli.py`, `tests/test_splitting.py` and `README.md`.