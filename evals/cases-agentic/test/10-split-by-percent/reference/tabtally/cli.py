"""Command line interface: add, list and balances."""

import argparse
import sys
from pathlib import Path

from tabtally import store
from tabtally.balances import net_balances
from tabtally.errors import MoneyError, TabtallyError
from tabtally.models import Expense
from tabtally.money import format_cents, parse_amount
from tabtally.splitting import split_by_percent, split_equally

DEFAULT_FILE = "tabtally.json"
USAGE_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tabtally", description="Track shared expenses.")
    parser.add_argument("--file", type=Path, default=Path(DEFAULT_FILE), help="expense file")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="record an expense")
    add.add_argument("--paid-by", required=True, metavar="NAME")
    add.add_argument("--amount", required=True, help="for example 12.50")
    add.add_argument("--description", required=True)
    sharing = add.add_mutually_exclusive_group(required=True)
    sharing.add_argument(
        "--with",
        dest="people",
        action="append",
        metavar="NAME",
        help="a person sharing the expense equally; repeat for each person",
    )
    sharing.add_argument(
        "--percent",
        action="append",
        metavar="NAME=PERCENT",
        help="split by percentage instead; repeat for each person, the percentages must add up to 100",
    )
    add.set_defaults(handler=_add)

    commands.add_parser("list", help="print all expenses").set_defaults(handler=_list)
    commands.add_parser("balances", help="print who owes whom").set_defaults(handler=_balances)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except TabtallyError as error:
        print(f"error: {error}", file=sys.stderr)
        return USAGE_ERROR


def _add(args: argparse.Namespace) -> int:
    cents = parse_amount(args.amount)
    if args.percent:
        shares = split_by_percent(cents, _parse_percents(args.percent))
    else:
        shares = split_equally(cents, args.people)
    expenses = store.load(args.file)
    expense = Expense(store.next_id(expenses), args.paid_by, args.description, cents, shares)
    store.save(args.file, [*expenses, expense])
    print(f"added #{expense.id}: {format_cents(cents)} for {args.description}")
    return 0


def _parse_percents(pairs: list[str]) -> dict[str, int]:
    percents: dict[str, int] = {}
    for pair in pairs:
        name, _, value = pair.partition("=")
        if not name or not value.isdigit():
            raise MoneyError(f"expected NAME=PERCENT with a whole number, got {pair!r}")
        if name in percents:
            raise MoneyError(f"listed more than once: {name}")
        percents[name] = int(value)
    return percents


def _list(args: argparse.Namespace) -> int:
    for expense in store.load(args.file):
        print(f"#{expense.id} {expense.payer} paid {format_cents(expense.cents)} for {expense.description}")
    return 0


def _balances(args: argparse.Namespace) -> int:
    for person, cents in sorted(net_balances(store.load(args.file)).items()):
        print(f"{person} {format_cents(cents)}")
    return 0
