# logscan

Reads structured log lines from stdin and prints how many lines, timestamps, `key=value` pairs and bare words it
saw. The nightly import runs it over log dumps of several gigabytes, so the tokenizer is on the hot path: it
borrows every token from the input line and does not allocate.

```console
$ printf '[2024-05-01T12:00:00Z] level=info msg="started \\"worker\\"" user=ann\n' | logscan
lines: 1
rejected lines: 0
timestamps: 1
pairs: 3
words: 0
```

## Line format

```text
[2024-05-01T12:00:00Z] level=info msg="disk 91% full" retries= done
```

- `[...]` is a timestamp. It is kept as written, without the brackets.
- `key=value` is a pair. The value is bare (up to the next space or tab, may be empty) or double-quoted. A quoted
  value may contain spaces and the escapes `\"`, `\\`, `\n` and `\t`; it is handed out as written, escapes
  included. `logscan::unescape` resolves them for callers that need the text.
- Anything else up to the next space or tab is a word.
- Tokens are separated by spaces or tabs. The first malformed token ends the line's token stream with an error.

## Development

```console
cargo test
```
