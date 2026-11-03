The relay now refuses to start on a bad config. It prints every problem with the file name and exits with status 2 before it reads any messages. The test suite passes (19 of 19, up from 9) and I checked the real `Main` entry point against bad, missing, and valid files.

For the typo from last week, `worker.threads=4a` now fails with:

```
Relay not started: invalid configuration in config.properties (2 problems):
  - worker.threads must be a whole number, got '4a'
  - metrics.enabled must be true or false, got 'ture'
```

What changed in `ConfigLoader`, which was the source of the silent fallbacks:
- **Bad values** (non-numbers, values below the minimum, bad timeout units, and misspelled booleans) are errors. They used to fall back to defaults or `false`.
- **Upstream URL** must be an absolute http or https URL. A malformed or missing URL used to become `null`.
- **Missing or unreadable file** is an error. It used to be treated as an empty config.
- **Unknown keys** are errors. A misspelled key name such as `worker.thread` used to be ignored.
- **All problems are reported together** in one message, not one per restart.

`Main` catches the error, prints it to stderr, and exits with status 2. I also added a short note to the README.

Decisions for you to check:
- **Unknown keys are rejected.** This is the part most likely to break an existing deployment, if any `config.properties` has extra keys. If you'd rather only warn, that is a one-line change.
- **Upstream must be http or https.** Tell me if other schemes are valid for you.
- **Exit status is 2.** Any non-zero status would also work, so change it if your ops tooling expects something else.

Not handled: a key that appears twice in the file still silently keeps the last value. Catching that means parsing the file myself, so I left it out.

Nothing is committed. The changes are in `ConfigLoader.java`, `Main.java`, `ConfigLoaderTest.java`, and `README.md`.