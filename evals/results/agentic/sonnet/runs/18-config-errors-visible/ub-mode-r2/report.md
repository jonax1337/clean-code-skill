The relay now refuses to start on a bad configuration. It prints every problem to stderr and exits with status 78. All 17 tests pass, and I ran it by hand twice. A file with `worker.threads=4x` gives exit 78 and this message:

```
relay refuses to start. Invalid configuration in bad.properties:
  - worker.threads must be a whole number of at least 1, but is '4x'
```

`config.example.properties` still starts normally.

I committed this locally as `424ba4d`. I did not push it, and I did not run the crapper, dryer or mutator tools from the skill.

**What the relay now rejects**
- **Unreadable file:** a missing or unreadable config file used to mean it ran on defaults. Now it refuses to start.
- **Bad numbers:** `worker.threads`, `queue.capacity` and `retry.max-attempts` must be whole numbers within their minimums.
- **Bad timeout:** `request.timeout` must be a number followed by `ms`, `s` or `m`, and it can't overflow.
- **Bad flag:** `metrics.enabled` must be exactly `true` or `false`. Before, `yes` quietly meant false.
- **Bad upstream:** `upstream.url` must be present and be an http or https URL. A missing one used to crash with a null pointer.
- **Unknown keys:** a misspelled key such as `worker.thread=8` is now an error, because it would otherwise be ignored the same way the typo'd value was.

If several things are wrong, they are all listed in one message. Optional keys that are absent still use their defaults.

**Behaviour change:** any existing `config.properties` with extra or misspelled keys will now fail to start. That is the intent, but check your deployed configs before rolling this out.

I replaced the two tests that expected the old fallback behaviour with tests for the new rejections. I also added a short note to the README.

**Log**
- Read the loader, `Main`, its tests and the README.
- Wrote the failing tests first and saw them fail for the expected reasons.
- Rewrote `ConfigLoader` and made `Main` print the error and exit.
- Fixed two mistakes along the way: the shell mangled a regex backslash, and one of my overflow test values didn't actually overflow.
- Updated the README and committed.