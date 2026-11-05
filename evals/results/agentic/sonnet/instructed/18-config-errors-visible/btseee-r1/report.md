The relay now refuses to start on a bad configuration. It prints every problem to stderr and exits with code 78, so a deploy script or init system sees the failure. The full suite passes (16 tests). I also started the relay by hand with `worker.threads=4x`. It printed this and exited with 78:

```
Invalid configuration in ...\bad.properties:
  - worker.threads must be a whole number, got '4x'
```

**Why it happened:** `ConfigLoader` replaced any bad value with its default. That covered non-numeric or too-small numbers and malformed timeouts. A missing or unreadable file also ran on defaults. Booleans were worse: `metrics.enabled=yes` silently became `false`.

**What's rejected now** (all problems reported together, not one per restart):
- Numbers that aren't whole numbers, or are below the minimum (`worker.threads` and `queue.capacity` need at least 1, `retry.max-attempts` at least 0).
- Timeouts without a unit (`30`), with a bad unit, too large to represent, or zero.
- `metrics.enabled` set to anything other than `true` or `false`.
- A missing or unreadable config file.
- `upstream.url` missing, malformed, or not an absolute URL with a host. A missing one used to cause a `NullPointerException`.
- Unknown keys, for example `worker.thread=8`. A misspelled key would otherwise have been ignored without any message. The error lists the valid keys.

Defaults still apply when a key is absent, so `config.example.properties` and the README need no change.

The changes are in `ConfigLoader.java`, `ConfigException.java` (it now builds the multi-line message) and `Main.java` (it catches the exception and exits). I replaced the two tests that asserted the old fall-back-to-default behaviour with tests for the new rejections.

Unknown keys are now fatal. If any existing `config.properties` carries leftover or commented-in keys the relay doesn't read, those deployments will fail on the next start. That is the intended outcome, but check the production files before rolling this out.

I haven't committed anything.