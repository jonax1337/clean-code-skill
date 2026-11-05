The relay now refuses to start when its configuration is wrong. It prints every problem it finds to stderr and exits with status 2. The full test suite passes (19 tests), and I tried the behavior by hand:

```
relay: refusing to start. Invalid configuration in ...\bad.properties:
  - metrics.enable is not a known setting (known: [api.token, metrics.enabled, ...])
  - worker.threads must be a whole number of at least 1, was '1o'
exit=2
```

A valid config (the example file) still starts normally and exits 0.

**What used to fall back silently and now stops startup** (`ConfigLoader.java`):
- **Numbers** (`worker.threads`, `queue.capacity`, `retry.max-attempts`) that aren't a number or are below their minimum. This is the case that hit ops.
- **`request.timeout`** without a valid unit (e.g. `30`), or set to zero.
- **`metrics.enabled`** set to anything except `true` or `false`. Before, a typo like `ture` quietly turned metrics off.
- **`upstream.url`**: missing, or not an http/https URL with a host. Before, a missing URL crashed internally, was caught, and left the upstream unset without any error.
- **A missing or unreadable config file.** Before, the relay ran on defaults and only failed later with a misleading "api.token is required".
- **Unknown keys** such as `worker.thread=8`. This is the same kind of mistake as last week's: a misspelled key name meant the setting was ignored and the default used.

**Other details:**
- All problems are reported at once, so a deploy doesn't take several fix-and-retry rounds.
- The error never prints the API token.
- `Main.java` catches the config error and exits with code 2, which is separate from a crash, so deploy scripts can tell the two apart.
- Defaults still apply when a key is left out entirely.
- The README now describes this behavior, and the timeout row says "positive".

**Things to check before rolling out:**
- **Stricter validation can block existing deployments.** A config with a stray or legacy key, or a value the old code was quietly ignoring, will now refuse to start. That's the point, but it's worth running each environment's `config.properties` through the new build before you deploy.
- **I rejected a zero timeout,** which the old README didn't rule out. It seemed clearly wrong, but tell me if anyone relies on it.
- **Two old tests changed.** They asserted the fallback-to-default behavior that was the bug, so I replaced them with tests that expect rejection. I also added tests for each new check.

Nothing is committed yet. Tell me if you'd like a commit or a PR.