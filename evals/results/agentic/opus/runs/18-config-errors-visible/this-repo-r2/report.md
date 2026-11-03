If the config is wrong now, the relay refuses to start. It prints every problem to stderr and exits with status 2, so the deploy fails where people will see it.

**What was wrong:** `ConfigLoader` replaced every bad value with a default. That covered numbers containing letters, numbers below the minimum, a timeout with no unit, and an unreadable or missing file. A bad or missing `upstream.url` quietly became `null`. A `metrics.enabled` value other than `true` (like `yes`) quietly became `false`. Misspelled key names were ignored too, so `worker.thread=8` would have run on 4 workers just like last week's typo did.

**What changed:**
- **`ConfigLoader`:** it gathers every problem and throws one `ConfigException` that names the file. It now rejects:
  - a file it can't read
  - unknown keys
  - missing or blank `upstream.url` or `api.token`
  - an `upstream.url` that isn't an http(s) URL with a host
  - numbers that aren't whole numbers or are below their minimum
  - badly formatted or overflowing timeouts
  - a `metrics.enabled` that isn't `true` or `false`

  Defaults still apply when a key is absent.
- **`Main`:** catches the error and prints it without a stack trace. With a typo'd config it shows:
  ```
  relay: refusing to start. Invalid configuration in ...\bad.properties:
    - unknown key worker.thread (expected one of [api.token, ...])
    - worker.threads: "4x" is not a whole number
    - metrics.enabled: "yes" is not true or false
  ```
  Values are quoted in the message except `api.token`, so the secret never appears in the output.
- **README:** a short paragraph explaining this behaviour.

**Tests:** `java tools/RunTests.java` gave 9 passed before the change and 21 passed after. Two existing tests asserted the old fall-back-to-default behaviour (`fallsBackToDefaultWorkerCountWhenNotANumber` and `...TimeoutWhenTheUnitIsMissing`). I replaced them with tests that expect a rejection, since that fallback is the bug. I also ran `Main` by hand: a bad config and a missing file each exit with 2, and the example config starts normally.

**Worth knowing before you deploy:**
- Any `config.properties` that currently has an extra key (an old setting, say) or a bad value will now stop the relay at startup. Run it once against your real config before rolling it out.
- A missing config file used to fail with a misleading "api.token is required"; it now says it can't read the file.
- I left `request.timeout=0s` allowed, because the README doesn't forbid it. If zero should be invalid, that's a one-line change.

Nothing is committed.