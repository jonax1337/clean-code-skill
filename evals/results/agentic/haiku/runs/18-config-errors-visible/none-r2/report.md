The relay now refuses to start on a bad `config.properties`. It prints every problem to stderr and exits with status 2. The incident case (`worker.threads=4a`) is now a hard failure, not a silent fall back to 4 workers.

**What was wrong:** `ConfigLoader` swallowed every bad value and substituted a default. That covered a non-numeric or too-small worker count, a malformed timeout, an unparseable URL, and a missing file. It also ignored unknown keys, so a typo in a key name was lost without a trace.

**What it does now:**
- **Bad values stop startup.** A non-number, a value below the minimum, a timeout without a unit, a boolean other than true/false, or a non-http(s) `upstream.url` is an error. The message names the key and quotes the value, for example `worker.threads: '4a' is not a whole number`.
- **Unknown keys stop startup.** `worker.thread=8` is reported as an unknown key, so the typo can't be ignored.
- **Missing file stops startup.** The message suggests copying `config.example.properties`.
- **All problems are reported at once,** so the file can be fixed in one pass.
- **Exit status 2** with the message on stderr, instead of a stack trace.
- **Optional keys that are absent** still take their defaults.

**Verification:**
- The test suite passes: 15 of 15. Six tests are new, and two old tests that asserted the fallback behavior now assert rejection.
- I ran the real entry point. The bad file exits 2 with the expected message, the missing file exits 2, and a valid file and `config.example.properties` both run normally.

**Choices I made that you may want to change:**
- **Unknown keys are an error.** This is strict. Any existing `config.properties` with a stray key will now refuse to start. That is the point, but check your deployed files before rollout.
- **`upstream.url` must be http or https.** Previously any URI passed.
- **Boolean parsing is case-insensitive.** `TRUE` and `True` are accepted. `yes`, `1` and typos are rejected.

I also updated the README with a short section on the validation behavior and the exit code. Nothing is committed yet. The changes are in the working tree across four files: `ConfigLoader.java`, `Main.java`, `ConfigLoaderTest.java` and `README.md`.