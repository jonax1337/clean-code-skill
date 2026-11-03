from datetime import date

import pytest

from hourlog.cli import main
from hourlog.entries import Entry
from hourlog.importer import ImportFormatError, parse_entries

ACME = "2025-03-03,Acme,60\n"
GLOBEX = "2025-03-04,Globex,90\n"
EXPECTED = [Entry(date(2025, 3, 3), "Acme", 60), Entry(date(2025, 3, 4), "Globex", 90)]


@pytest.mark.parametrize(
    "lines",
    [
        pytest.param([ACME, "\n", GLOBEX], id="in-the-middle"),
        pytest.param([ACME, GLOBEX, "\n"], id="at-the-end"),
        pytest.param([ACME, GLOBEX, "\n", "\n", ""], id="several-at-the-end"),
        pytest.param(["\n", ACME, GLOBEX], id="at-the-start"),
        pytest.param([ACME, "\r\n", GLOBEX, "\r\n"], id="windows-line-endings"),
        pytest.param([ACME, "   \n", GLOBEX, "\t\n"], id="only-whitespace"),
        pytest.param(iter([ACME, "\n", GLOBEX]), id="any-iterable"),
    ],
)
def test_blank_lines_are_skipped(lines):
    assert parse_entries(lines) == EXPECTED


def test_a_file_of_only_blank_lines_has_no_entries():
    assert parse_entries(["\n", "", "  \n"]) == []


@pytest.mark.parametrize(
    ("lines", "number"),
    [
        pytest.param([ACME, "\n", "2025-03-04,Globex\n"], 3, id="missing-minutes-after-blank"),
        pytest.param([ACME, "\n", "\n", "2025-03-04,Globex,Inc,90\n"], 4, id="unquoted-comma-after-blanks"),
        pytest.param(["\n", "2025-13-01,Acme,60\n"], 2, id="bad-date-after-blank"),
        pytest.param([ACME, "2025-03-04,Globex,abc\n", "\n"], 2, id="bad-minutes-before-blank"),
        pytest.param([ACME, "\n", "garbage\n"], 3, id="one-field"),
        pytest.param([ACME, "\n", "2025-03-04,,60\n"], 3, id="empty-project"),
        pytest.param([ACME, "\n", "2025-03-04,Globex,-5\n"], 3, id="negative-minutes"),
    ],
)
def test_malformed_lines_still_fail_with_their_physical_line_number(lines, number):
    with pytest.raises(ImportFormatError, match=rf"line {number}\b"):
        parse_entries(lines)


@pytest.fixture
def run(tmp_path, capsys):
    def invoke(*argv):
        code = main(["--file", str(tmp_path / "hourlog.json"), *argv])
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return invoke


def test_cli_imports_a_file_with_blank_lines(run, tmp_path):
    csv_file = tmp_path / "export.csv"
    csv_file.write_bytes(b"2025-03-03,Acme,60\r\n\r\n2025-03-04,Acme,30\r\n\r\n\r\n")
    code, out, err = run("import", str(csv_file))
    assert (code, out, err) == (0, "imported 2 entries\n", "")
    assert run("report")[1] == "Acme 1h30\n"


def test_cli_rejects_a_malformed_row_after_blank_lines_and_stores_nothing(run, tmp_path):
    csv_file = tmp_path / "export.csv"
    csv_file.write_text("2025-03-03,Acme,60\n\n\n2025-03-04,Acme\n", encoding="utf-8")
    code, _, err = run("import", str(csv_file))
    assert code == 1
    assert err.startswith("error: line 4")
    assert run("report")[1] == ""
