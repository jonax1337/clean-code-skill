The relay now refuses to start when its configuration is wrong. It prints every problem it finds to stderr and exits with status 78. All 18 tests pass, and I also ran it by hand against a bad file, a missing file and the example config. This is what a deployer sees now:

```
relay: refusing to start, invalid configuration in /etc/relay/config.properties:
  - metrics.enable: unknown key (check the spelling; known keys are api.token, metrics.enabled, ...)
  - worker.threads: must be a whole number of at least 1, got "1o"
exit=78
```

**Was there anything else that failed silently?** Yes. Besides the worker count, `ConfigLoader` had several other ways of quietly using a fallback value. Each of these now stops startup:
- **Bad numbers:** `worker.threads`, `queue.capacity` and `retry.max-attempts` used their defaults if the value wasn't a number *or* was below the minimum (e.g. `worker.threads=0`).
- **Bad timeout:** a `request.timeout` with no unit or a bad format (e.g. `30`) became 30s.
- **Bad metrics flag:** `metrics.enabled=yes` or `=on` became `false`.
- **Missing file:** if the config file was missing or unreadable, the relay ran on defaults.
- **Bad upstream URL:** a missing `upstream.url` crashed with a NullPointerException, and an invalid one became `null`. It must now be an absolute `http`/`https` URL.

**Choices you might want to change:**
- **Unknown keys are rejected.** A misspelled key name like `worker.thread=8` causes the same silent fallback as a bad value, so it's now an error too. The catch: any config file in your environments that has extra keys will stop starting until they're removed. It's easy to drop this check if you'd rather not.
- **A zero timeout is rejected.** `request.timeout=0s` means "time out immediately", so I treat it as a mistake.
- **Exit code 78** is the standard Unix code for a configuration error, so scripts and supervisors can tell it apart from a crash. The token's value never appears in error messages.

**Changes:**
- `ConfigLoader.java` checks every key before it builds the config.
- `ConfigException.java` now holds the full list of problems.
- `Main.java` prints that list and exits.
- In `ConfigLoaderTest.java`, the two tests that expected silent fallback now expect errors, plus 10 new tests.
- `README.md` describes the new behavior.

Nothing is committed yet.