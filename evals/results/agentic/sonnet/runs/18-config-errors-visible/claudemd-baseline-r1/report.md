The relay now refuses to start on a bad config. It prints every problem it found to stderr and exits with code 1. All 14 tests pass. I also ran it by hand with `worker.threads=4x`. It printed `relay: refusing to start. Invalid configuration in …: worker.threads must be a whole number, got '4x'` and exited 1.

The cause was in `ConfigLoader`, which replaced any bad or missing value with its default. It did the same when the config file itself was missing or unreadable. Now each of these is an error:
- **Numbers:** a non-number, or a value below the minimum, for `worker.threads`, `queue.capacity` or `retry.max-attempts`.
- **Timeout:** a bad `request.timeout` (no unit, an unknown unit, zero, or too large).
- **Boolean:** a `metrics.enabled` value that isn't exactly `true` or `false`.
- **URL:** a missing or malformed `upstream.url`. It used to become null, so a bad URL would have slipped through too.
- **Missing or unreadable file:** an error naming the file.
- **Typo'd key names:** unknown keys are now rejected, such as `worker.thread=8`. A misspelled key name was the same silent-defaults problem as a bad value.

Because of that last rule, any extra keys in an existing production `config.properties` will now stop startup. Check the real config against the seven documented keys before deploying.

The changes are in `ConfigLoader.java` and `Main.java`. I replaced the two tests that expected the old fall-back behaviour with tests for each rejection above, plus a test that several errors are reported together. Nothing is committed.