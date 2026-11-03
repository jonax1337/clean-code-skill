The relay now refuses to start on a bad configuration. It prints every problem it found and exits with status 1. All 15 tests pass, and I ran it by hand with `worker.threads=4o`:

```
Invalid configuration in ...\bad.properties:
  - worker.threads: '4o' is not a whole number >= 1
Refusing to start.
```

I committed this locally as `1a8dda3` and did not push.

**What was wrong:** the loader silently fell back to defaults in more places than the worker count. A missing or unreadable file, an out-of-range number, a timeout with no unit and a non-boolean `metrics.enabled` all did it. A missing `upstream.url` crashed with a `NullPointerException` instead of a useful message.

**What it rejects now:**
- A missing or unreadable config file.
- A non-numeric or out-of-range `worker.threads`, `queue.capacity` or `retry.max-attempts`.
- A `request.timeout` that isn't like `500ms`, `30s` or `2m`.
- A `metrics.enabled` that isn't exactly `true` or `false`.
- A missing `api.token`, or a missing or malformed `upstream.url` (it must be an absolute http(s) URL).
- Unknown keys, such as `worker.thread=8`. This goes beyond a typo in a value: a typo in a key name was silently ignored for the same reason. If ops have any extra keys in their files today, the relay will now refuse to start until they're removed.

Keys that are absent still use their defaults. The changes are in `ConfigLoader.java` and `Main.java`, and I added one sentence about the strict validation to the README. I replaced the two tests that asserted the old fall-back behaviour with ones that expect rejection.

I didn't run the crapper, dryer or mutator tools from the skill, because they aren't in the repo.