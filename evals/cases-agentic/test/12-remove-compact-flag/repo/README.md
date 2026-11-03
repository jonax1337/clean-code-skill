# tabulate

Aligns delimited text from stdin into a plain-text table.

```console
$ printf 'id,name\n7,Ann\n10,Bob\n' | tabulate --header
id  name
--  ----
7   Ann
10  Bob
```

## Options

| Option | Description |
| --- | --- |
| `-d`, `--delimiter <CHAR>` | Cell delimiter, or `tab` (default `,`) |
| `-H`, `--header` | Underline the first row |
| `-b`, `--border` | Draw `\|` between the columns |
| `-w`, `--max-width <N>` | Cut cells longer than N characters |
| `-c`, `--compact` | **Deprecated, will be removed in 1.0.** Print rows without padding |
| `-h`, `--help` | Show the usage text |

## Development

```console
cargo test
```
