The relay now refuses to start on a bad configuration, and the error message lists every problem it found. All 14 tests pass. I also ran the real entry point against a deliberately bad file, and it printed the errors below and exited with status 2 without reading any input:

```
relay: refusing to start: invalid configuration in ...bad.properties:
  - upstream.url must be an http or https URL with a host, but was 'ftp:/x'
  - worker.threads must be a whole number, but was '4x'
```

I haven't committed anything.

The cause was in `ConfigLoader`. A value that was present but wrong silently became the default. So `worker.threads=4x` ran with 4 workers and no warning.

**What the relay now rejects at startup:**
- **Bad values:** non-numeric or out-of-range numbers (`worker.threads=0`, `retry.max-attempts=-1`), timeouts with no unit (`30`) or a zero timeout, and `metrics.enabled` set to anything other than `true` or `false`.
- **Missing or malformed settings:** a missing or unreadable config file, a missing `api.token` or `upstream.url`, and an `upstream.url` that isn't an http(s) URL with a host.
- **Unknown keys:** for example a misspelled `worker.thread`. This is the same kind of silent failure as the typo that bit you, so I included it.

Defaults still apply, but only to keys that are absent.

Three behaviour changes could affect existing deployments:
- **Missing file:** a missing `config.properties` used to fall through to defaults. Now it's an error.
- **`metrics.enabled`:** this was previously lenient, so `yes` or `TRUE` counted as false or true by `Boolean.parseBoolean`. Now only exactly `true` or `false` is accepted.
- **Unknown keys:** a config file that happens to contain an extra key will fail until the key is removed.

Check any live config files against these before the next deploy.

The changes are in `ConfigLoader.java`, `Main.java` (prints the error and exits with status 2), the tests, and a short README note. I replaced the two old tests that expected silent fallback and added tests for each rejection.