# hourlog

A tiny time log. Record the minutes you spent per project, import them from a CSV file and see totals per project.

```console
$ python -m hourlog log --day 2025-03-03 --project Acme --minutes 90
logged 90 minutes for Acme
$ python -m hourlog import export.csv
imported 12 entries
$ python -m hourlog report
Acme 14h30
Globex 3h05
```

All commands accept `--file PATH` before the command name (default `hourlog.json`).

## CSV import

One entry per line, three comma-separated fields:

```text
2025-03-03,Acme,90
2025-03-04,Globex,45
```

The date is `YYYY-MM-DD` and the minutes are a positive whole number. A line that cannot be read stops the import with an error that names the line, and nothing is stored.

## Development

```console
python -m pytest
```
