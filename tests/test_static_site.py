import json
from pathlib import Path

from scripts.build_static_site import build_static_data


def test_static_site_payload_is_complete_and_anonymous(tmp_path):
    output = tmp_path / "appointments.json"
    payload = build_static_data(output, rows=120)
    saved = json.loads(output.read_text(encoding="utf-8"))

    assert payload["metadata"]["synthetic"] is True
    assert payload["metadata"]["seed"] == 42
    assert payload["metadata"]["represents_real_hospital"] is False
    assert "Python" in payload["metadata"]["source"]
    assert saved["metadata"]["rows"] == 120
    assert len(saved["records"]) == 120
    assert set(saved["records"][0]) == {"d", "p", "h", "w", "r", "s", "n", "t", "ci", "rm", "cl"}
    assert "patient_id" not in output.read_text(encoding="utf-8")


def test_static_site_entrypoint_exists():
    root = Path(__file__).parents[1]
    assert (root / "docs" / "index.html").exists()
    assert (root / "docs" / "assets" / "site.js").exists()
    assert (root / "docs" / "assets" / "site.css").exists()
