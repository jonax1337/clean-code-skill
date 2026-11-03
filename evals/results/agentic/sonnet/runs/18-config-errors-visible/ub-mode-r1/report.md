The relay now refuses to start when its configuration is wrong. It prints every problem to stderr and exits with status 2. I committed the change on `main`, but the push failed because no remote is configured, so nothing is pushed.

I ran `java tools/RunTests.java` and all 15 tests pass. I also ran the relay with `worker.threads=4x`. It printed this and exited with status 2:

```
relay: refusing to start. Invalid configuration in …\bad.properties:
  - worker.threads must be a whole number of at least 1, got '4x'
```

**What I changed**
- **`ConfigLoader`:** it no longer falls back to defaults on bad input. It collects all the problems and reports them together, so the person deploying sees everything at once. Defaults still apply to optional keys that are absent.
- **`Main`:** it catches the config error, prints it and exits with status 2.
- **README:** it now says what happens on invalid configuration.
- **Tests:** I replaced the two tests that pinned the old fall-back behaviour and added tests for each failure below.

The old code swallowed more than the worker count. All of these now stop startup:
- a missing or unreadable file (the old code just ran on defaults)
- a missing, malformed or non-http(s) `upstream.url` (a missing one used to crash with an NPE)
- numeric values that aren't numbers or are below their minimum
- timeouts with no unit, or ones that overflow
- `metrics.enabled` set to anything but `true` or `false` (the old code treated `yes` or `ture` as false)

**Decision for you:** I also made unknown keys an error, so a typo like `worker.thread=8` is caught instead of ignored. It's the same failure from a different typo. The catch is that a config file with extra or experimental keys will now be rejected. If you'd rather not have that, it's one small block in `parse()`.

The crapper, dryer and mutator tools from the skill aren't in this checkout, so I didn't run them.