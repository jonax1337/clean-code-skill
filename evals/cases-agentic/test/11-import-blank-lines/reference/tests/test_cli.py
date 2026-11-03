import pytest

from hourlog.cli import main


@pytest.fixture
def run(tmp_path, capsys):
    def invoke(*argv):
        code = main(["--file", str(tmp_path / "hourlog.json"), *argv])
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return invoke


def test_log_records_minutes(run):
    code, out, _ = run("log", "--day", "2025-03-03", "--project", "Acme", "--minutes", "90")
    assert code == 0
    assert out == "logged 90 minutes for Acme\n"


def test_import_stores_every_entry(run, tmp_path):
    csv_file = tmp_path / "export.csv"
    csv_file.write_text("2025-03-03,Acme,90\n2025-03-04,Acme,30\n2025-03-04,Globex,45\n", encoding="utf-8")
    code, out, _ = run("import", str(csv_file))
    assert code == 0
    assert out == "imported 3 entries\n"
    assert run("report")[1] == "Acme 2h00\nGlobex 0h45\n"


def test_import_of_a_bad_file_stores_nothing(run, tmp_path):
    csv_file = tmp_path / "export.csv"
    csv_file.write_text("2025-03-03,Acme,90\n2025-03-04,Acme,soon\n", encoding="utf-8")
    code, _, err = run("import", str(csv_file))
    assert code == 1
    assert err.startswith("error: line 2")
    assert run("report")[1] == ""


def test_import_skips_blank_lines(run, tmp_path):
    csv_file = tmp_path / "export.csv"
    csv_file.write_text("2025-03-03,Acme,90\n\n2025-03-04,Acme,30\n\n", encoding="utf-8")
    code, out, _ = run("import", str(csv_file))
    assert code == 0
    assert out == "imported 2 entries\n"
