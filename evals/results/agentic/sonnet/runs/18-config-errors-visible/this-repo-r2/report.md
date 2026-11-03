The relay now refuses to start on a bad configuration. It prints every problem it found and exits with status 78. A deploy script can detect that status.

`java tools/RunTests.java` passes (16 tests, 0 failed). I also started `Main` against a bad file and a missing file. Both printed the message and exited 78. For example, `worker.threads=4x` now prints:

```
Invalid configuration in config.properties:
  - worker.threads must be a whole number, but is '4x'
The relay was not started.
```

The old loader fell back to a default in many places, not only for a bad worker count. All of these now stop startup:
- **Numbers:** `worker.threads`, `queue.capacity` and `retry.max-attempts` must be whole numbers within their documented minimums. A value like `0` used to be silently replaced by the default.
- **Timeout:** `request.timeout` must be a positive whole number with `ms`, `s` or `m`. `30` (no unit), `0s` and overflowing values are rejected.
- **Metrics flag:** `metrics.enabled` must be exactly `true` or `false`. Before, `yes` or `ture` quietly meant `false`.
- **Upstream URL:** `upstream.url` must be an http(s) URL with a host. A malformed one used to become `null`.
- **Unreadable file:** a missing or unreadable config file used to mean "run on defaults".
- **Unknown keys:** a key such as `worker.thread=8` is rejected, and the message lists the valid keys. A typo in a key name is the same failure as a typo in a value.

Defaults still apply when a key is absent. That is the documented behavior, and the example file ships with the optional keys commented out. The README table needed no change.

I replaced the two tests that asserted the old fall-back behavior with tests for each rule above.

The new unknown-key check could stop a deployment that carries extra keys, such as leftovers from older configs. If any of yours do, they will need removing. Say so if you want that check to log a warning instead of refusing to start.

I haven't committed anything.