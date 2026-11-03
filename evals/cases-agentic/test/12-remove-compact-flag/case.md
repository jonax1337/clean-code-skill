# Remove a deprecated CLI flag (Rust)

Tests whether the agent removes a deprecated option completely and cleanly: the short alias, the help text, the code that only the option used (the compiler flags leftovers as dead-code warnings), its tests, the README row and a changelog entry, while keeping the helpers other options still need and leaving history in the changelog alone.

## Prompt

`--compact` has been deprecated since 0.8 and we said it would go in 1.0, so let's take it out now. The tests should still pass afterwards.
