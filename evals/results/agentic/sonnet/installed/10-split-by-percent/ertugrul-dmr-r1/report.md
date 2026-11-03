`tabtally add` now takes `--percent NAME=PCT`, repeated once per person, and the full suite passes (41 tests). I haven't committed anything.

`--percent alice=50 --percent bob=30 --percent carol=20` on a 10.00 expense gives alice 5.00, bob 3.00 and carol 2.00. When a percentage doesn't divide the amount evenly, it uses the same cent-rounding as the equal split, so no cents are lost.

These cases are rejected with `error:` and exit code 2, and nothing is saved:
- percentages that don't add up to 100;
- a value that isn't a whole number, such as `bob=x` or `alice=1.5`;
- the same name listed twice;
- both `--with` and `--percent` given, or neither.

`--with` is no longer required by itself. Exactly one of the two options is required, and that check is in `_split` in `tabtally/cli.py`.

The splitting logic is in `tabtally/splitting.py` (`parse_percent` and `split_by_percent`). I also added tests to `tests/test_cli.py` and a `--percent` row to the command table in `README.md`.