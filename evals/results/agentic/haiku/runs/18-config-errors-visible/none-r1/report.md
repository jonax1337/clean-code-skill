The relay now refuses to start on any bad configuration, and it tells you what is wrong. All 18 tests pass (9 existing, 9 new), and I checked the behavior by running the real `Main` with bad and good config files.

For the failure you described, `worker.threads=4x` now produces:

```
invalid configuration in C:\...\bad.properties; the relay will not start:
  - worker.threads must be a whole number, got '4x'
```

It exits with status 2 and processes no messages.

**What changed**

- **`ConfigLoader.java`**: every value is validated and no bad value falls back to a default. Problems are collected and reported together in one message. A key that is absent still gets its default.
- **`Main.java`**: a `ConfigException` prints the message to stderr and exits with status 2, with no stack trace.
- **`ConfigLoaderTest.java`**: the two tests that asserted the silent fallback now assert rejection. I added tests for each rejection path, for reporting several problems at once, and for a missing file.
- **`README.md`**: documents that the relay checks the whole file before starting.

**Choices I made that you may want to change**

- **Unknown keys are rejected.** A typo like `worker.thread=8` was previously ignored silently. This could break a deployment that has extra keys in its file, so check before rolling it out.
- **`upstream.url` must be an absolute http or https URL with a host.** Previously any string was accepted, including a missing value.
- **A zero `request.timeout` is rejected.**
- **`metrics.enabled` must be `true` or `false`**, case-insensitively. Anything else used to count as false.
- **A missing config file is an error.** Previously a missing file meant the loader ran on defaults.
- **The API token is never echoed** into error messages.

**Not covered**

- A key listed twice in the file still silently takes the last value. Catching that would mean replacing `java.util.Properties` parsing, so I left it alone.

Nothing is committed. Say if you want a commit, and I'll use the attribution line from the reminder.