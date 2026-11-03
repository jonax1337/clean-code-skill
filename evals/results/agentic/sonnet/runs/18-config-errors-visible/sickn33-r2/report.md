The relay now refuses to start on bad configuration. All 15 tests pass. I also ran it by hand with `worker.threads=4x`, and it printed the message below and exited with status 78:

```
Invalid configuration in …\bad.properties:
  - worker.threads must be a whole number, but was '4x'
Refusing to start.
```

**What now stops the relay:**
- **Missing file:** a missing or unreadable `config.properties` used to mean it ran on defaults. Now it's an error.
- **Bad numbers:** a non-number or an out-of-range value in `worker.threads`, `queue.capacity` or `retry.max-attempts`.
- **Bad timeout:** `request.timeout` with no unit, a zero value, or a value too large to use.
- **Bad boolean:** a `metrics.enabled` value other than `true` or `false`. Before, a typo like `yes` quietly meant `false`.
- **Bad upstream URL:** a missing or malformed `upstream.url`, or one that isn't an http(s) URL with a host. A missing one used to crash with a null-pointer error.
- **Unknown keys:** a misspelt key like `worker.thread`. This is the same kind of silent-default mistake as your typo, so I included it.

The relay lists every problem in one run, so whoever deploys it doesn't have to fix them one at a time. Defaults still apply to optional keys that are absent.

The changes are in `ConfigLoader.java` and `Main.java`. I replaced the two tests that asserted the old fall-back behaviour and added tests for each rejection. I also added a short note on strict validation to the README.

**Behaviour changes to be aware of:**
- A config that used to start with a quietly ignored mistake now won't start. That includes any stray or old keys in existing `config.properties` files, so check those before the next deploy.
- A zero timeout is now rejected. That's my judgment call, and it's easy to relax if you want it allowed.
- The exit status is 78, the BSD "configuration error" code. It's a constant in `Main.java` if your tooling expects a different one.

I haven't committed anything.