The relay now refuses to start when the configuration is wrong. It prints every problem at once to stderr and exits with status 78, which is the standard "configuration error" code, so a supervisor or deploy script can tell a bad config apart from a crash. All 21 tests pass with no compiler warnings, and I ran the relay by hand against a bad file, a good file and a missing file.

Here's what it prints for last week's kind of mistake:

```
relay: refusing to start, invalid configuration in C:\...\bad.properties
2 configuration problems:
  - metrics.enable is not a recognised key (misspelled?); known keys are [api.token, metrics.enabled, ...]
  - worker.threads must be a whole number of at least 1, got '1O'
```

**What changed**
- **Defaults only apply to keys that are left out.** If a key is present but its value is wrong, that's now an error instead of a silent fallback to the default. This covers numbers that don't parse or are out of range, empty values, timeouts with no unit or too large to represent, and `metrics.enabled` values other than `true`/`false`. Before, anything that wasn't `true` (like `yes`) quietly meant false.
- **Other silent fallbacks I found are now errors too:**
  - A missing or unreadable config file used to start the relay on defaults; it now fails.
  - A missing `upstream.url` used to crash with a bare NullPointerException; it now gets a proper message.
  - A malformed `upstream.url` used to be accepted as empty; it now has to be an http(s) URL with a host.
- **The API token is never included in error messages**, and a test checks this.
- The main change is in `ConfigLoader.java`. `ConfigException` now carries the full list of problems, and `Main` prints them and exits. The README says which mistakes stop startup, and I replaced the two old tests that expected the silent fallback with tests for each rejection.

**Before you roll this out**
- **Misspelled key names are now rejected.** If someone writes `worker.thread=8`, the setting is silently ignored and the default is used, which is the same failure you just had, so I made it an error. The catch is that any deployed config with an extra key (an old setting, a key another tool reads) will also stop the relay from starting. That's the point, but check your configs before deploying. If you'd rather only warn on unknown keys, it's a one-line change.
- A `request.timeout` of `0s` is still accepted, because the README doesn't set a minimum. If zero should be rejected, I can add that.

I haven't committed anything; the changes are in your working tree.