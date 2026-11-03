The relay now refuses to start on a bad configuration. It prints every problem it finds to stderr and exits with status 2 before processing any messages. The 16 tests pass (9 existing, 7 new), and I ran the real `Main` against a bad file to confirm the output.

For the typo from last week, `worker.threads=four` now produces:

```
invalid configuration in config.properties:
  - worker.threads: 'four' is not a whole number
The relay was not started. Fix the configuration and try again.
```

**What changed**

- **`ConfigLoader.java`:** the silent fallbacks are gone. A missing optional key still takes its default. A key that is present but wrong is an error. That covers:
  - a missing or unreadable file, and a file that cannot be parsed
  - a missing `upstream.url` or `api.token`
  - `upstream.url` that is not an absolute URL
  - integers that are not numbers, or are below their minimum
  - timeouts without a unit, or zero
  - `metrics.enabled` values other than `true` or `false`
- **Unknown keys are now errors.** A misspelled key such as `queue.capcity` used to be ignored silently, which is the same failure mode as the incident, so I treated it as a configuration error too. If any existing deployment has extra keys in its file, it will now fail to start until they are removed.
- **`Main.java`:** a configuration error prints the message to stderr and exits with status 2, with no stack trace.
- **`ConfigLoaderTest.java`:** the two tests that asserted the old fallback behavior now assert rejection. I added cases for each rule above and one that checks all problems are reported together.
- **`README.md`:** a short paragraph describes the new startup behavior.

**Choices I made that you may want to change**

- A zero `request.timeout` is rejected. This is stricter than the old code, and I think it is right.
- Exit status is 2. Any non-zero code would stop a deployment script that checks the exit status.

**Not done**

- I did not commit anything. The changes are in the working tree.
- The `serialVersionUID` compiler warning on `ConfigException` was already there. I left it alone.