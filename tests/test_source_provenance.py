from pathlib import Path
from urllib.parse import urlparse

from data_utils import load_csv, validate_labour_data


def test_bundled_labour_data_has_expected_observations_and_official_sources():
    csv_path = Path(__file__).resolve().parents[1] / "data" / "labour_indicators.csv"
    with csv_path.open("r", encoding="utf-8") as csv_file:
        raw = load_csv(csv_file)
    df = validate_labour_data(raw)

    assert df["Period"].tolist() == ["2025 Annual", "2026 Q1", "2026 Q2"]
    assert df["Labour force participation (%)"].tolist() == [49.4, 49.2, 50.0]
    assert df["Unemployment (%)"].tolist() == [3.9, 3.7, 4.0]
    assert df["Period"].is_unique

    # Provenance fields must be present and point to the official DCS domain.
    assert {"Source", "Source URL"}.issubset(raw.columns)
    assert raw["Source"].astype(str).str.strip().ne("").all()
    parsed = raw["Source URL"].map(urlparse)
    assert parsed.map(lambda item: item.scheme == "https").all()
    assert parsed.map(lambda item: item.hostname == "www.statistics.gov.lk").all()
    assert parsed.map(lambda item: item.path.startswith("/LabourForce/StaticalInformation/")).all()

    expected_paths = [
        "/LabourForce/StaticalInformation/Bulletins/",
        "/LabourForce/StaticalInformation/QuarterlyReports/",
        "/LabourForce/StaticalInformation/QuarterlyReports/",
    ]
    assert parsed.map(lambda item: item.path).tolist() == expected_paths
