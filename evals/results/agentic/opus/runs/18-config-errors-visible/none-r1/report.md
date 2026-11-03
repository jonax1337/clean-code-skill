The relay now refuses to start when the configuration is wrong. It lists every problem it finds on stderr and exits with status 78, the standard exit code for a configuration error. All 19 tests pass, and I ran it against a config with last week's kind of typo:

```
relay: refusing to start, invalid configuration in ...\bad.properties:
  - worker.threads must be a whole number of at least 1, but was "1O"
  - unknown key "metrics.enable" (known keys: api.token, metrics.enabled, queue.capacity, ...)
```

A missing file now fails the same way, and the example config still starts and relays normally.

**What used to fall back to defaults silently and is now an error** (`ConfigLoader.java`):
- **Numbers:** `worker.threads`, `queue.capacity` and `retry.max-attempts` are rejected if they aren't numbers, are below their minimum, or are too large.
- **Timeout:** `request.timeout` is rejected without a valid unit (`30`, `5h`), if it's zero, or if it's too large.
- **Metrics flag:** `metrics.enabled` must be exactly `true` or `false` (any capitalisation). Before, `yes` or `on` quietly meant `false`.
- **Upstream URL:** `upstream.url` is checked as well. A missing value used to crash with a `NullPointerException`, and a bad one ran with no upstream at all. It's now required and must be an http(s) URL with a host.
- **Missing file:** if the config file can't be found, the relay stops. Before, it carried on as if the file were empty.

Defaults still apply to optional keys that are left out entirely, just never in place of a bad value.

**Two decisions for you:**
- **Unknown keys are errors.** A misspelled key name (`worker.thread=8`) leads to the same outage as a bad value, so I made it fail too. If ops ever adds their own keys to this file for other tools, that will now block startup. The fix is a one-line change if you'd rather just warn.
- **Exit code 78.** Check that whatever starts the relay in production (systemd, k8s, etc.) treats a non-zero exit as a failed deploy and doesn't just restart it in a loop.

I also changed `Main.java` to print a clean message instead of a stack trace and noted the strict checking in the README. Two old tests asserted the fallback behaviour, so I rewrote them to expect errors and added tests for each case above. Nothing is committed yet.