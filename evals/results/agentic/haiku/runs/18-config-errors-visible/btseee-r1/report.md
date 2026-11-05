The relay now refuses to start on any bad configuration. It prints every problem at once to stderr and exits with status 2 before it touches any messages. All 19 tests pass, and I ran `Main` against a typo'd config, a missing file, and a valid config to confirm the output.

With your bad file, the output is:

```
Refusing to start: invalid configuration in ...\bad.properties:
  - worker.threads: 'four' must be a whole number, at least 1
  - request.timeout: '30' must be a whole number followed by ms, s or m, for example 30s
```

**What was silently falling back before, and what happens now:**
- **Invalid values** (`worker.threads=four`, `worker.threads=0`, an empty value) used to fall back to the default. They are now errors.
- **Timeouts without a unit** (`request.timeout=30`) used to fall back to 30s. They are now errors.
- **`metrics.enabled`** with anything other than `true`/`false` (e.g. `yes`) used to mean `false`. It is now an error.
- **`upstream.url`** that was missing or malformed became `null` with no error. It is now required and must be an absolute `http://` or `https://` URL.
- **A missing config file** used to be treated as an empty file. It is now an error that names the path.

**Choices I made beyond your request, so you can redirect me:**
- **Unknown keys are refused.** A misspelled key like `worker.thread=8` was silently ignored, which is the same failure mode as the incident. The error lists the valid keys.
- **Only `http`/`https` URLs are accepted** for `upstream.url`. Say so if you need another scheme.
- **Exit status is 2** for a bad configuration, so a supervisor or deploy script can detect it.
- **The API token is never echoed** in error messages.

**Before you deploy:** any existing `config.properties` with an extra key or a bad value will now refuse to start. That is the intended behavior, but check the live files first so the change doesn't surprise anyone.

**Changed files:** `ConfigLoader.java` (rewritten validation), `Main.java` (catches the error and exits), `ConfigLoaderTest.java` (two tests that asserted the old fallback now expect a refusal, plus new cases for each check), and a short note in `README.md`. Nothing is committed.