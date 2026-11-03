The relay now refuses to start when `config.properties` is wrong. It prints every problem it finds and exits with status 2 before processing any input. I didn't commit anything.

I ran it against a bad file (`worker.threads=4o`), a missing file, and the example config with a real token. The bad and missing files were refused with exit 2, and the valid one ran. The JUnit suite passes: 17 of 17, up from 9.

What changed, in `ConfigLoader`:
- **Wrong values fail instead of defaulting.** `worker.threads=four`, `0` for a minimum-1 key, `request.timeout=30` with no unit, and `metrics.enabled=yes` are all errors. Omitted optional keys still use their defaults.
- **`upstream.url` is validated.** It must be present and an `http` or `https` URL. It was previously unchecked despite the README calling it required.
- **Missing or unreadable files are errors.** Previously they were silently treated as empty.
- **Unknown keys are errors.** A typo like `worker.thread=8` used to be ignored. This is the one change that could affect an existing deployment: a `config.properties` with any extra key will now refuse to start. If you'd rather only warn on unknown keys, tell me and I'll switch it.
- **All problems are reported together.** One run shows everything that's wrong, not one error per restart.

`Main` prints `Refusing to start: ...` to stderr and exits with 2. I also updated the two tests that pinned the old fallback behavior, added tests for each new rule, and added a short paragraph to the README.