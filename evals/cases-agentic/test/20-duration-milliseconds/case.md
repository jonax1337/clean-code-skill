# Duration parser switches from seconds to milliseconds (TypeScript)

Tests an API change with several callers: the return unit of a shared function changes, and callers that never multiply (a threshold comparison, an HTTP header, a log line) compile and pass the visible tests but silently break.

## Prompt

`parseDuration` in `src/duration.ts` returns seconds, so everything that wants milliseconds multiplies by 1000. Change it to return milliseconds and adapt the rest of the code to that.
