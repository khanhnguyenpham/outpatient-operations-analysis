import pandas as pd

from ops_analysis.analysis import calculate_kpis
from ops_analysis.data import generate_appointments, validate


def test_generated_data_passes_validation():
    frame = generate_appointments(rows=400, seed=7)
    assert validate(frame) == []
    assert frame["appointment_id"].is_unique


def test_no_show_denominator_excludes_cancellations():
    frame = pd.DataFrame({
        "status": ["Completed", "No-show", "Cancelled"],
        "no_show": [0, 1, 0],
        "wait_minutes": [10.0, None, None],
    })
    result = calculate_kpis(frame)
    assert result["no_show_rate_pct"] == 50.0

