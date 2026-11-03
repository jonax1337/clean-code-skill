`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. The full suite passes (48 tests), including new ones for the splitting and the CLI. I haven't committed anything.

- **Split:** `split_by_percent` in `tabtally/splitting.py` uses the existing `allocate`, so the shares always add up to the exact amount in cents. For example, 10.00 at 50/30/20 gives 5.00, 3.00 and 2.00.
- **Duplicate check:** I moved it into a shared helper, `_reject_duplicates`, so the equal split and the percentage split use the same check.
- **`--with` or `--percent`:** `--with` is no longer required on its own. `add` now needs exactly one of the two, and using both is a usage error.
- **Rejected input:**
  - Malformed values such as `alice`, `alice=`, `=50`, `alice=12.5` or `alice=-5` exit with code 2 and argparse's usage message.
  - Percentages that don't total 100 are rejected with `error: percentages must add up to 100, not N`. Nothing is saved.
  - A percentage of 0 is rejected, as is a name listed twice.
- **README:** I added a row for the new form to the command table.

Decision for you: I reject a 0% share instead of accepting it, because someone with no share wouldn't need to be listed. Say if you'd rather allow it.