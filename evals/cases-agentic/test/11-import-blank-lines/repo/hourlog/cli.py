"""Command line interface: log, import and report."""

import argparse
import sys
from datetime import date
from pathlib import Path

from hourlog import store
from hourlog.entries import Entry
from hourlog.importer import ImportFormatError, parse_entries
from hourlog.report import format_duration, totals_by_project

DEFAULT_FILE = "hourlog.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hourlog", description="A tiny time log.")
    parser.add_argument("--file", type=Path, default=Path(DEFAULT_FILE), help="log file")
    commands = parser.add_subparsers(dest="command", required=True)

    log = commands.add_parser("log", help="record time for a project")
    log.add_argument("--day", type=date.fromisoformat, default=None, help="YYYY-MM-DD, default today")
    log.add_argument("--project", required=True)
    log.add_argument("--minutes", type=int, required=True)
    log.set_defaults(handler=_log)

    import_ = commands.add_parser("import", help="import entries from a CSV file")
    import_.add_argument("csv_file", type=Path)
    import_.set_defaults(handler=_import)

    commands.add_parser("report", help="print the total per project").set_defaults(handler=_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (ImportFormatError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


def _log(args: argparse.Namespace) -> int:
    entry = Entry(args.day or date.today(), args.project, args.minutes)
    store.append(args.file, [entry])
    print(f"logged {entry.minutes} minutes for {entry.project}")
    return 0


def _import(args: argparse.Namespace) -> int:
    with args.csv_file.open(encoding="utf-8") as lines:
        entries = parse_entries(lines)
    store.append(args.file, entries)
    print(f"imported {len(entries)} entries")
    return 0


def _report(args: argparse.Namespace) -> int:
    for project, minutes in sorted(totals_by_project(store.load(args.file)).items()):
        print(f"{project} {format_duration(minutes)}")
    return 0
