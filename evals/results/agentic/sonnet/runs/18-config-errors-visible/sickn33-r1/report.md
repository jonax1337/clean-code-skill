The relay now refuses to start on bad configuration. A `worker.threads=4x` typo prints this and exits with status 2:

```
Invalid configuration in config.properties:
  - worker.threads: '4x' is not a whole number
Refusing to start.
```

All 17 tests pass, and I ran that `4x` case against the built `Main` to confirm the output and exit code. I haven't committed anything.

The cause was `ConfigLoader` swallowing every parse error and returning the default. I rewrote it so it collects every problem and reports them together, so the deployer fixes them in one pass. `Main` prints the list to stderr, exits with status 2, and processes no input.

The old code had other silent fallbacks, so I closed those too:
- **Missing or unreadable file:** it used to run on defaults, and now it's an error.
- **Bad numeric values:** `worker.threads`, `queue.capacity` and `retry.max-attempts` fail on non-numbers, blank values and values below their minimum.
- **`request.timeout`:** it fails if the unit is missing, the number overflows, or the value is zero.
- **`metrics.enabled`:** only `true` or `false` is accepted. Before, any typo silently meant false.
- **`upstream.url`:** it must be present and an absolute URL with a host. A missing or invalid value used to cause a `NullPointerException` or a null URL.
- **Unknown keys:** a misspelled key like `worker.thread=8` is rejected, because it would otherwise be ignored and the default used, which is the same failure you had.

Two behaviors are new:
- **Zero timeout:** `request.timeout=0s` is now rejected, since it would fail every delivery. Say so if you want it allowed.
- **Stray keys:** any key outside the seven documented ones now stops startup. A config file that carries extra keys for other tooling will fail on the first deploy.

I replaced the two tests that asserted the old fallback with tests for each rejection, and added a short note on the strict behavior to the README.