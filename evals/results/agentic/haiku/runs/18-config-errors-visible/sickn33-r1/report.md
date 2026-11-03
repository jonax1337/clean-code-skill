The relay now refuses to start on a bad configuration. It prints every problem to stderr and exits with status 2. The full test suite passes (16/16), and I ran the real entry point against a typo'd file to confirm the output.

For last week's case, `worker.threads=4x` now produces:

```
Not starting: the configuration is invalid.
  - worker.threads: must be a whole number, got '4x'
```

**What changed**

- **`ConfigLoader`:** nothing falls back to a default silently anymore. These now fail the load:
  - a missing or unreadable config file
  - a non-numeric or out-of-range `worker.threads`, `queue.capacity` or `retry.max-attempts`
  - a `request.timeout` without a valid unit
  - a missing or non-absolute `upstream.url`
  - a `metrics.enabled` value other than `true` or `false`
  - a missing `api.token`
  - an unknown key, such as `worker.thread`
  
  All problems are collected and reported together, not one at a time.
- **`Main`:** catches the configuration error, prints it, and exits with code 2.
- **Tests:** the two existing tests that asserted silent fallback now assert rejection. I added tests for each new rule and for reporting multiple errors at once.
- **README:** a short paragraph under the config table describes the new behavior.

**Choices I made that you may want to change**

- **Unknown keys are rejected.** A misspelled key name is the same failure as a misspelled value, so I treated it as an error. The catch is that any existing `config.properties` with an extra or obsolete key will now stop the relay. Check deployed files before rolling this out.
- **`upstream.url` must be an absolute URL with a host.** I did not restrict the scheme to http/https. Tell me if you want that.
- **`request.timeout=0s` is still accepted.** The spec didn't say otherwise, so I left it alone.

Nothing is committed. The changes are in the working tree: `Main.java`, `ConfigLoader.java`, `ConfigLoaderTest.java`, and `README.md`.