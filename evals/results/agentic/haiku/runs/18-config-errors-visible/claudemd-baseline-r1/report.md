The relay now refuses to start when its configuration is wrong. It prints every problem to stderr and exits with status 2. The incident case, `worker.threads=4a`, now fails with:

```
relay: invalid configuration in config.properties:
  - worker.threads must be a whole number of at least 1, got '4a'
relay: not started. Fix the configuration above and start again.
```

The 20 tests pass (up from 9), and I ran the real entry point with a bad config (exit 2) and a good one (runs normally).

**What changed**
- **`ConfigLoader`** no longer falls back to defaults for bad values. It rejects:
  - a missing config file, which used to run on defaults;
  - a non-numeric or out-of-range `worker.threads`, `queue.capacity` or `retry.max-attempts`;
  - a `request.timeout` with no unit or an unknown unit;
  - a `metrics.enabled` that is not `true` or `false`;
  - an `upstream.url` that is not an absolute http or https URL (it used to become `null`);
  - an empty value, and a missing `api.token`.
- **Every problem is reported in one message**, so a deployer fixes everything in one pass.
- **`Main`** prints the error to stderr and exits with status 2 instead of starting.
- **`ConfigLoaderTest`**: the two tests that asserted silent fallback now assert rejection. I added tests for each new rule and for the report-all behavior.
- **`README.md`**: a short paragraph now describes the new behavior.

**Decisions you may want to revisit**
- **Unknown keys are now errors.** A misspelled key such as `worker.thread=8` is the same failure as a misspelled value, so I rejected it too. Any existing config with extra keys will stop starting until those keys are removed.
- **Optional keys with empty values are errors** (`queue.capacity=`), not defaults.
- **Exit code 2** is my choice; the code is a constant in `Main` if your ops tooling expects something else.

**Not done**
- I have not committed anything.
- I did not add a test for `Main`'s exit path. I checked it by running the program instead.