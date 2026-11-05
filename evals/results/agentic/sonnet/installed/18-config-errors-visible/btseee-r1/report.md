The relay now refuses to start on a bad config. It prints every problem to stderr and exits with status 1 before reading any input. All 15 tests pass, including the new rejection cases. I didn't run `Main` by hand against a bad file, so the exit-1 path in `Main` itself isn't covered by a test.

Example of what a deployer sees:
```
Invalid configuration in config.properties:
  - worker.threads must be a whole number, but was '4x'
  - request.timeout must be a number followed by ms, s or m (e.g. 30s), but was '30'
Relay not started.
```

**What now fails startup** (`ConfigLoader.java`):
- **Bad values:** a non-numeric or out-of-range number, a timeout without a valid unit, or a `metrics.enabled` that isn't exactly `true` or `false`.
- **Upstream URL:** a missing `upstream.url`, or one that isn't an http(s) URL with a host. Before, a bad URL became `null` and surfaced later.
- **Unreadable file:** a missing or unreadable config file. Before, the relay ran on defaults with no warning.
- **Unknown keys:** a typo like `worker.thread=8` is rejected. Otherwise the typo would still leave the default in place without any message.

All problems are collected and reported together, so one deploy attempt shows everything wrong. `Main.java` catches the error and exits 1.

**Behaviour changes:**
- Configs that used to start may now be rejected. For example, `metrics.enabled=yes` used to count as false, and stray keys were ignored.
- Check existing deployed `config.properties` files before rolling this out.
- Defaults still apply when an optional key is absent. They no longer apply when a key is present but wrong.

I replaced the two old tests that asserted the silent fallback, added tests for each rejection case, and added a short note on startup validation to `README.md`. Nothing is committed.