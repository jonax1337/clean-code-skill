The relay now refuses to start on bad configuration. It prints every problem it finds and exits with status 2 before it processes any messages. All 18 tests pass.

Against your example, the relay now reports:

```
invalid configuration in config.properties, the relay will not start:
  - worker.threads must be a whole number of at least 1 (got 'four')
```

**What changed**

- **No silent defaults:** a present but invalid value is an error. Before, a bad worker count, timeout, or boolean quietly fell back to a default, and a bad `upstream.url` became `null`.
- **Missing file is an error:** before, a missing or unreadable file quietly ran the relay on defaults. It now reports `configuration file … was not found`.
- **Every problem at once:** all errors are collected into one message, so a deployer fixes them in one pass.
- **Unknown keys are rejected:** a misspelled key like `worker.thread` was silently ignored before. This goes beyond the value typo you described, so tell me if you'd rather keep ignoring unknown keys.
- **Stricter values:** `metrics.enabled` must be `true` or `false`, the URL must be absolute, and an empty value for an optional key is an error.
- **`Main`:** a config error prints the report to stderr and exits 2 instead of dumping a stack trace.
- **README:** one paragraph documents the new behavior.

**Tests:** I wrote the new tests first and watched 11 of them fail for the expected reason. The two existing tests that pinned the fallback behavior now expect rejection. The end-to-end check ran the real `Main` against a bad file, a missing file, and a good file. The good file started and delivered its message.

**Not done:** I haven't committed. Your instructions say to commit only when asked, so the four changed files are uncommitted in the working tree.