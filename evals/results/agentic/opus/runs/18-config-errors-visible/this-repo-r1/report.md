The relay now refuses to start when the configuration is wrong. It prints every problem it finds to stderr and exits with status 78. A worker count like `worker.threads=1O` gets this:

```
Invalid configuration in …\config.properties:
  - worker.threads: '1O' is not valid, expected a whole number of at least 1
The relay did not start.
```

**What changed**
- **`ConfigLoader`**: the loader used to fall back to defaults silently in five places. All of them are now errors:
  - a missing or unreadable config file
  - an `upstream.url` that isn't a valid http(s) URL (it used to become `null`)
  - numbers that don't parse, are too large for an int, or are below their minimum
  - timeouts without a unit, or too large to convert to milliseconds
  - `metrics.enabled` values other than `true`/`false` (`ture` used to mean `false`)
- Problems are collected and reported together, so a deploy doesn't need several rounds of fixing. Errors never print the `api.token` value.
- Defaults still apply when a key is absent or commented out. A key that is present with an empty value is an error.
- **`Main`**: catches the config error and prints the message instead of a stack trace. Exit code 78 is the conventional "configuration error" code, so deploy scripts can tell it apart from a crash.
- **README**: documents this behavior.

**One addition you should know about:** misspelled keys are now rejected too, e.g. `metrics.enabld=true` → "unknown key". Otherwise a typo'd key name runs silently on the default, which is the same failure you had last week. The catch: a production `config.properties` with stray or obsolete keys will now fail to start. Check the real files before rolling this out.

**Tests:** I replaced the two existing tests that asserted the old fallback-to-default behavior and added tests for each validation rule, including the boundaries (each number at its minimum is accepted, one below is rejected). `java tools/RunTests.java`: 21 tests found, 21 successful, 0 failed. I also ran `Main` by hand: a bad config and a missing file each exited with 78 and the messages above, and `config.example.properties` exited with 0 and forwarded the message normally.

**Left alone:** `request.timeout=0s` is still accepted, because the README doesn't say whether zero is allowed. If zero is meaningless for your upstream client, that's a one-line rule to add. The compiler's `serialVersionUID` warning on `ConfigException` was there before this change.

Nothing is committed yet.