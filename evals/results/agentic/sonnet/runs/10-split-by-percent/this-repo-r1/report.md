`tabtally add` now takes `--percent NAME=PCT`, so `--percent alice=50 --percent bob=30 --percent carol=20` splits an expense by percentage. `python -m pytest` runs 50 tests and all pass. I didn't run a linter or type checker.

**What changed**
- **Options:** `--with` and `--percent` are now mutually exclusive, and you must give exactly one. Using both, or neither, is a usage error with exit code 2.
- **Validation:** it rejects percentages that don't total 100, naming the actual total (`percentages must add up to 100, got 90`). It also rejects anything that isn't a whole number, a missing name or `=`, a percentage of 0 or less, and a name listed twice. These all exit with code 2 and an `error:` message.
- **Rounding:** the split uses the existing cent allocation, so the shares always add up to the full amount. A $10.01 expense split 33/33/34 still sums to $10.01.
- **Code:** the logic is in `tabtally/splitting.py` (`parse_percent`, `split_by_percent`, and a shared duplicate-name check). The option is wired in `tabtally/cli.py`.
- **Docs and tests:** I added a README row and tests in `tests/test_splitting.py` and `tests/test_cli.py`.

I also decided to reject a 0% entry rather than allow it. That is a judgement call. If you want 0% to be allowed, it's a one-line change.

My script first rewrote the files with Windows line endings. I converted them back to LF, so the diff contains only the intended changes.