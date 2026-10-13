"""CSV imports consume a leading UTF-8 BOM, not an in-cell character."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "skills/productivity/xlsx/scripts"


def run(script, *args):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", timeout=30, check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
@pytest.mark.parametrize("flags", [(), ("--no-infer", "--plain")])
def test_csv_import_preserves_headers_without_signature(tmp_path, encoding, flags):
    source, workbook = tmp_path / "source.csv", tmp_path / "output.xlsx"
    source.write_text("Name,Amount\nАлиса,007\ninside\ufefftext,8\n", encoding=encoding)
    run("csv_to_xlsx.py", source, workbook, *flags)
    rows = run("xlsx_read.py", workbook, "--json")["rows"]
    assert rows[0] == ["Name", "Amount"]
    assert rows[1] == ["Алиса", "007" if "--no-infer" in flags else 7]
    assert rows[2][0] == "inside\ufefftext"


def test_explicit_csv_encoding_is_preserved(tmp_path):
    source, workbook = tmp_path / "source.csv", tmp_path / "output.xlsx"
    source.write_text("Name;Amount\nAndré;7\n", encoding="cp1252")
    run("csv_to_xlsx.py", source, workbook, "--encoding", "cp1252", "--delimiter", ";")
    assert run("xlsx_read.py", workbook, "--json")["rows"] == [
        ["Name", "Amount"], ["André", 7],
    ]
