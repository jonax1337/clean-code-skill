# Split an expense by percentage (Python)

Tests whether the agent adds a feature in the way the codebase already works: money stays in whole cents, the split goes through the existing allocation helper so no cent is lost to rounding, invalid input is reported through the project's error convention without saving anything, and the README, tests and existing behavior are kept consistent.

## Prompt

Add a `--percent NAME=PCT` option to `tabtally add` so an expense can be split by percentage instead of equally, for example `--percent alice=50 --percent bob=30 --percent carol=20`. The percentages are whole numbers and should add up to 100.
