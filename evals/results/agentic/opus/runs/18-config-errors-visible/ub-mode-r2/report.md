If the configuration is wrong in any way, the relay now refuses to start. It prints every problem at once to stderr and exits with status 78, the standard "configuration error" code. All 20 tests pass, and I ran it by hand against real files:

```
relay: refusing to start. Invalid configuration in ...\bad.properties:
  - workers.threads: unknown key (known keys: [api.token, metrics.enabled, ...])
  - worker.threads: '1O' is not valid, expected a whole number, at least 1
  - metrics.enabled: 'ture' is not valid, expected true or false
exit=78
```

A missing file also stops it with exit 78, and the example config relays as before (exit 0).

**What was wrong:** the worker count wasn't the only gap. The loader quietly used defaults or blank values for almost any mistake:
- a number that wasn't a number, or was below its minimum (e.g. `worker.threads=0`)
- a timeout without a unit (`request.timeout=30`)
- a misspelled flag (`metrics.enabled=ture` became `false`)
- a missing or unreadable config file (it ran on defaults)
- a missing or broken `upstream.url` (it started with no upstream at all)
- a misspelled key name (`worker.thread=8` was ignored)

Defaults now apply only to keys that are left out entirely.

**Changes:**
- `ConfigLoader.java`: checks every key and collects all the problems before failing.
- `Main.java`: catches the error, prints the clear message instead of a stack trace, and exits with 78.
- `README.md`: documents the new behaviour.
- `ConfigLoaderTest.java`: 11 new tests. I wrote them first and confirmed all 11 failed against the old code before fixing it. The two old tests that expected a silent fallback now expect the relay to refuse.

**Two stricter rules you may want to check:**
- **Unknown keys are rejected.** This catches typos in key names, which would cause the same silent fallback. But a deployment that keeps extra keys in `config.properties` will now fail to start.
- **A timeout of `0` is rejected.** The README didn't say whether zero was allowed, and zero usually means "no timeout" or a mistake.

Either can be loosened in one line.

**Log:**
1. Read the repo and listed every place the loader quietly fell back.
2. Wrote the new tests. My first attempt broke the file's line endings, so I rewrote it, then saw the 11 failures.
3. Rewrote the loader and got all 20 tests passing. Small cleanup in one helper.
4. Changed `Main` and ran the relay by hand with a bad config, a missing file and the example config.
5. Updated the README and committed (`ce8d7e0`) on `main`.

**Not done:**
- I didn't push, because the repo has no remote.
- I skipped the crapper, dryer and mutator steps. Those tools aren't in the skill folder or the repo.
- There's no automated test for `Main`'s exit code, because `System.exit` can't be tested cleanly without restructuring `Main`. The manual runs above cover it.