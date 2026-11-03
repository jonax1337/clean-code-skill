The relay now refuses to start when its configuration is wrong. It prints every problem it found and exits with status 78, the standard "configuration error" exit code, so supervisors and deploy scripts will see a failed start. All 20 tests pass, and I ran it by hand to check the output. Here's what a deployer sees with a config like last week's:

```
Invalid configuration in C:\...\c.properties:
  - metrics.enable is not a known setting (check the spelling)
  - worker.threads must be a whole number of at least 1, but was '1O'
The relay was not started.
```

The worker count wasn't the only case where a bad value quietly became a default. Each of these now stops startup:

- **Number settings** (`worker.threads`, `queue.capacity`, `retry.max-attempts`): rejected if they aren't a whole number or are below their minimum.
- **`request.timeout`**: rejected if the unit is missing (`30` instead of `30s`) or the number is too large.
- **`metrics.enabled`**: anything other than `true` or `false` is rejected. Before, `yes` or `ture` quietly meant false. Capitalisation still doesn't matter.
- **`upstream.url`**: rejected if it's missing or isn't an `http(s)://` URL with a host. A missing URL used to crash with a NullPointerException, and a bad one was quietly dropped.
- **Missing or unreadable config file**: now reported directly. Before, the relay quietly fell back to all defaults.
- **Misspelled key names**, like `worker.thread=8`: now rejected. These were ignored, so the default was used without any sign. It's the same kind of failure as last week's.

The fix is mainly in `src/main/java/com/acme/relay/config/ConfigLoader.java`. `Main.java` prints the problems and exits instead of showing a stack trace. The README describes the new behaviour. Two tests asserted the old fallbacks; I replaced them with tests for the rejections, along with tests for each case above.

**Before you deploy:** a config that used to start might now be rejected, for example because of an empty `worker.threads=`, an extra key that isn't a relay setting, or a non-HTTP upstream URL. That's intended, but run the new build against your real `config.properties` files first, so the first rejection doesn't happen during a deploy.

I haven't committed anything.