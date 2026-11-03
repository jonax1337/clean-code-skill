The relay now refuses to start on a bad configuration. It prints every problem to stderr and exits with status 78. `java tools/RunTests.java` passes (17 of 17). I also ran `Main` against a file with `worker.threads=4x` and against a missing file. Both printed a clear message and exited 78.

The old loader fell back to defaults in every one of these cases:
- **Number settings:** a non-number, or a value below the minimum.
- **`request.timeout`:** a bad format (such as no unit) or a value too large to represent.
- **Missing config file:** the relay ran on all defaults.
- **`upstream.url`:** a missing or invalid value became `null`, or crashed with a `NullPointerException` when absent.

Changes:
- **`ConfigLoader`:** it now collects all problems and reports them in one `ConfigException`. A typical message looks like `worker.threads must be a whole number, but is '4x'`.
- **Stricter than before:**
  - **Unknown keys:** these are rejected, so a typo'd key name like `worker.thread=8` is caught too.
  - **`metrics.enabled`:** it must be `true` or `false`. Before, `ture` silently meant `false`.
  - **`upstream.url`:** it must be an absolute URL with a host.
- **`Main`:** it prints the error and exits 78. Defaults still apply to keys that are absent.
- **Tests and README:** the two old tests that expected fallback now expect rejection, and I added tests for each failure case. The README documents the new behavior.

Before you deploy, check that no existing `config.properties` relies on a quietly ignored value. That includes stray keys, `metrics.enabled=yes`, or a timeout without a unit. Those files will now fail to start.

I chose exit status 78 (the Unix "configuration error" code, `EX_CONFIG`) myself. It's one constant in `Main` if you'd rather use 1.