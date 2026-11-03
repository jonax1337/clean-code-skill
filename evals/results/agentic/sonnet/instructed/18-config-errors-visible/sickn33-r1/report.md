The relay now refuses to start on a bad configuration, prints every problem to stderr, and exits with status 2. All 15 tests pass, and I ran the real `Main` against a bad file to confirm the output and exit code.

A typo like `worker.threads=4x` used to fall back to the default silently. Now it produces:

```
Invalid configuration in bad.properties:
  - unknown key 'worker.thread' (known keys: [...])
  - upstream.url must be an absolute http(s) URL with a host, but was 'ftp:/x'
  - worker.threads must be a whole number, but was '4x'
Refusing to start.
```

The main changes are in `ConfigLoader.java` and `Main.java`:
- **Every problem at once:** the loader collects all problems and reports them together, so the deployer fixes them in one pass.
- **Wrong values:** a malformed or out-of-range number, a timeout without a unit, or a `metrics.enabled` that isn't `true` or `false` is now an error. Defaults apply only to keys that are absent.
- **Missing or unreadable file:** this is now an error. Before, the relay ran on defaults, so a wrong path was silent too.
- **Misspelled key names:** unknown keys are rejected, so `worker.thread=8` is caught instead of being ignored.
- **`upstream.url`:** it must be an absolute http(s) URL with a host. Before, a bad URL became `null` and failed later.

I replaced the two tests that expected the old fall-back behavior and added tests for each rejection, including the all-at-once report. I also added a short README note.

Rejecting unknown keys and bad `metrics.enabled` values goes slightly beyond the typo you hit. A deployed `config.properties` with stray keys, or a value like `metrics.enabled=yes`, will now stop the relay. If you'd rather keep either lenient, it's a small change.

I haven't committed anything.