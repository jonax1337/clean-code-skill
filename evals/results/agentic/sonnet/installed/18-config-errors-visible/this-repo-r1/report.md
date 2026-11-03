The relay now refuses to start on bad configuration. It prints every problem it finds to stderr and exits with status 2 before reading any input. `java tools/RunTests.java` passes (19 tests, 0 failed). I also ran `Main` against a deliberately broken file. It printed:

```
Invalid configuration in …\bad.properties:
  - unknown key 'worker.thread'
  - worker.threads must be a whole number, but is '4x'
Refusing to start.
```

The defaults used to take over silently in several places, and I closed all of them:
- **Bad values:** a non-numeric or out-of-range `worker.threads`, `queue.capacity` or `retry.max-attempts` is now an error. So is a malformed `request.timeout` (for example `30` with no unit, or a number too large to represent), and any `metrics.enabled` that isn't exactly `true` or `false`. Before, `yes` silently meant false.
- **Blank values:** an optional key that is present but empty is an error. Defaults apply only to keys that are absent.
- **Unknown keys:** a misspelt key such as `worker.thread` is now an error. Without this, the typo would still have been ignored and the default used.
- **Unreadable file:** a missing or unreadable config file is an error. Before, the relay quietly ran on defaults, which is the worst case of the same bug.
- **`upstream.url`:** a missing or malformed value, or one that isn't an absolute URL with a host, is an error. Before, a missing one would have crashed with a `NullPointerException`.

The changes are in `ConfigLoader.java`, `ConfigException.java` and `Main.java`. `Main` catches the error and sets the exit code. I replaced the old "falls back to default" tests with ones asserting rejection, added tests for each new case, and added a short paragraph to the README.

- **Stricter than before:** any existing deployment with a sloppy value (`metrics.enabled=yes`, a stray unknown key, an empty `worker.threads=`) will now fail to start until it's fixed. That's the point, but check the production `config.properties` files before rolling this out.
- **Not committed:** I haven't made a commit.