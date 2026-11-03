The relay now refuses to start on a bad config. It prints every problem to stderr and exits with status 78. All 17 tests pass, and a manual run against a deliberately broken file behaved as intended:

```
Invalid configuration in ...\bad.properties:
  - unknown key 'worker.treads'
  - worker.threads must be a whole number, but was '4x'
Refusing to start. Fix the configuration and try again.
exit=78
```

The cause was in `ConfigLoader`. It swallowed every parse error and substituted the default. It also ignored a missing config file, and a missing or garbled `upstream.url` produced a null (or an NPE).

**What it now rejects:**
- **Bad numbers:** a non-numeric value like `4x`, a blank value, or one below its minimum, such as `worker.threads=0`.
- **Bad `request.timeout`:** no unit (`30`), zero, or an overflowing value.
- **Bad `metrics.enabled`:** anything other than `true` or `false`. Before, `yes` or `ture` silently meant false.
- **Bad `upstream.url`:** missing, malformed, or not an absolute http(s) URL.
- **Missing or unreadable config file:** this used to run on defaults.
- **Unknown keys:** a typo like `worker.treads=8` would otherwise be ignored and leave the default in place. I added this check because it's the same failure as last week's incident.

Defaults still apply to keys that are absent.

**Tests and docs:** I replaced the two tests that asserted the old fallback-to-default behaviour and added tests for each case above. I also added a short "Invalid configuration" section to the README.

**Strictness risk:** the unknown-key check is strict. A config file that currently contains stray or legacy keys will stop the relay from starting after this change. Check production files before rolling out. If you'd rather make that a warning, it's a small change.

I haven't committed anything.