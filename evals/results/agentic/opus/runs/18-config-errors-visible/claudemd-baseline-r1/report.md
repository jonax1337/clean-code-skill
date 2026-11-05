The relay now refuses to start when its configuration is wrong. It prints what's wrong to stderr and exits with status 2. With the kind of typo you had last week, the deploy now shows:

```
relay: refusing to start, invalid configuration in /etc/relay/config.properties:
  - worker.thread: unknown key (expected one of [api.token, metrics.enabled, ...])
  - worker.threads: '1O' is not a whole number
```

**The cause:** `ConfigLoader` threw away every bad value and quietly used the default instead. That went beyond the worker count: bad numbers, numbers out of range, timeouts without a unit, booleans like `yes`, and even a missing config file all fell back to defaults. A missing or invalid `upstream.url` didn't fail cleanly either.

**What changed:**
- **`ConfigLoader.java`:** Defaults now apply only when an optional key is left out entirely. If a key is present with a bad value, it's an error. The loader checks the whole file and reports every problem at once, so a deploy doesn't have to fail repeatedly to surface them one by one.
- **`Main.java`:** Catches the error, prints it and exits with status 2.
- **`ConfigException.java`:** Now holds the full list of problems.
- **README:** Describes the new behaviour.

**Checks I added that you might not expect:**
- **Unknown keys are rejected.** A misspelled key name like `worker.thread=8` would otherwise be silently ignored, which is the same failure as last week. Any extra keys in an existing `config.properties` will now stop the relay from starting.
- **A missing config file is an error**, instead of running on defaults.
- **`request.timeout=0s` is rejected.** The README only asks for "a whole number", so this is a new rule.
- **`upstream.url` must be an absolute http or https URL.**

Before rolling out, it's worth running the new build once against each environment's real config. Any config that was quietly broken before will now refuse to start.

**Tests:** I replaced the two existing tests that expected the old fall-back-to-defaults behaviour. I added a regression test for the `1O` worker count, tests for each kind of rejection, and a `MainTest` that checks a bad config gives exit status 2, a clear message, and no messages relayed. `java tools/RunTests.java` passes all 22 tests with no compiler warnings. I also ran the built relay by hand: a broken config produced the output above with exit status 2, and `config.example.properties` relayed a message and exited with 0.

I haven't committed anything.