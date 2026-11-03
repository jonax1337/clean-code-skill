`tabtally add` now accepts `--percent NAME=PCT`, so `--percent alice=50 --percent bob=30 --percent carol=20` splits an expense 50/30/20. All 51 tests pass. I wrote the new tests first and confirmed they failed before adding the code.

**How it works**
- **Choosing a split:** `--with` and `--percent` can't be used together, and you have to give one of them. Using both is rejected with argparse's usual usage error. Existing `--with` commands work exactly as before.
- **Rounding:** percentage splits use the same cent rounding as equal splits, so the shares always add up to the full amount. For example, 1 cent split 50/50 gives alice 1 cent and bob 0.

**What gets rejected** (each prints an `error:` message, exits with code 2 and saves nothing):
- Percentages that don't add up to 100. The message shows the actual total.
- Anything that isn't a plain whole number, such as `alice=12.5`, `alice=-5`, `alice=+5` or `alice=abc`, and input with no name or no number (`alice`, `=50`).
- The same person listed twice.

**Decision for you:** I also reject 0%, assuming that listing someone at 0% is a mistake. If you'd rather allow it, delete one check in `tabtally/splitting.py` and its test.

The code changes are in `tabtally/splitting.py` (new `split_by_percent` and `parse_percent`) and `tabtally/cli.py` (the new option). I also added a line about `--percent` to the commands table in the README. Nothing is committed yet.