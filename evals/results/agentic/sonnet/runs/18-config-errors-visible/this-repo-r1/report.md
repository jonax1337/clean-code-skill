The relay now refuses to start on bad configuration. It prints every problem it finds to stderr and exits with status 2. `java tools/RunTests.java` passes (19 tests, 0 failed).

I also ran the built relay against a deliberately bad file and against a missing file. Both printed the problems, then "The relay was not started.", and exited with 2. For a bad file the output looks like this:

```
Invalid configuration in …\bad.properties:
  - unknown key 'worker.thread' (known keys: …)
  - worker.threads must be a whole number, but is '4x'
The relay was not started.
```

**The cause.** `ConfigLoader` fell back to the default whenever a value was unparseable or out of range. That is how `worker.threads=4x` quietly became 4. The same fallback applied to a missing or unreadable file, and a bad `upstream.url` came back as `null`.

**What now stops startup:**
- A non-numeric value for `worker.threads`, `queue.capacity` or `retry.max-attempts`.
- A number below its minimum.
- A `request.timeout` without a valid unit, or one too large to represent.
- A `metrics.enabled` that isn't exactly `true` or `false`. Before, `yes` silently meant `false`.
- A missing `upstream.url`, or one that isn't an absolute URL with a scheme and host. Before, a missing `upstream.url` caused an NPE.
- A missing or unreadable config file.

**Unknown keys also fail now.** A typo in a key name, such as `worker.thread=8`, used to be ignored in the same silent way, so I made it an error that lists the valid keys. This is slightly beyond what you asked, but it is the same failure. If you'd rather allow extra keys, it's one method to remove (`reportUnknownKeys`).

A key that is absent still takes its default, as before.

**Changes:**
- The fix is in `ConfigLoader.java`.
- `Main.java` catches the error and exits with 2.
- I replaced the two tests that expected the old fallback behavior with tests for each rejection, plus one that checks all problems are reported together.
- I added a short paragraph to the README.

Any config file that only worked because of a silent fallback will now fail at startup. That is the intent, but check the deployed `config.properties` files before rolling this out.