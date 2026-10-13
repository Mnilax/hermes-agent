"""Elapsed durations must survive the XLSX reader's JSON boundary."""
import json
from pathlib import Path
import subprocess
import sys

SCRIPTS = Path(__file__).resolve().parents[2] / "skills/productivity/xlsx/scripts"


def test_duration_values_are_json_serializable_without_changing_other_types(tmp_path):
    workbook = tmp_path / "duration.xlsx"
    fixture = subprocess.run(
        [sys.executable, "-c", """
from datetime import date, timedelta
from openpyxl import Workbook
import sys
wb = Workbook()
wb.active.append([timedelta(hours=36, minutes=15), timedelta(seconds=-5),
                  7, True, date(2026, 1, 2)])
wb.save(sys.argv[1])
""", str(workbook)], capture_output=True, text=True, timeout=30, check=False,
    )
    assert fixture.returncode == 0, fixture.stderr
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "xlsx_read.py"), str(workbook), "--json"],
        capture_output=True, text=True, encoding="utf-8", timeout=30, check=False,
    )
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)["rows"]
    assert rows == [["1 day, 12:15:00", "-1 day, 23:59:55", 7, True, "2026-01-02T00:00:00"]]
    assert type(rows[0][2]) is int
    assert type(rows[0][3]) is bool
