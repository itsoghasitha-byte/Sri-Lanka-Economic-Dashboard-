from io import StringIO

import pandas as pd
import pytest

from data_utils import DataValidationError, calculate_change, load_csv, validate_labour_data


def valid_labour_df():
    return pd.DataFrame({
        "Period": ["2025 annual", "2026 Q1"],
        "Labour force participation (%)": [49.4, 50.0],
        "Unemployment (%)": [3.9, 4.0],
    })


def test_load_csv_accepts_valid_csv():
    df = load_csv(StringIO("period,value\n2026,12\n"))
    assert df.shape == (1, 2)
    assert df.loc[0, "value"] == 12


def test_load_csv_rejects_empty_csv():
    with pytest.raises(DataValidationError):
        load_csv(StringIO("Period,Value\n"))


def test_validate_labour_data_rejects_missing_required_column():
    df = valid_labour_df().drop(columns=["Unemployment (%)"])
    with pytest.raises(DataValidationError, match="Missing required column"):
        validate_labour_data(df)


@pytest.mark.parametrize("bad_value", [None, "not-a-number"])
def test_validate_labour_data_rejects_missing_or_non_numeric_values(bad_value):
    df = valid_labour_df().astype({"Unemployment (%)": "object"})
    df.loc[0, "Unemployment (%)"] = bad_value
    with pytest.raises(DataValidationError, match="Missing or non-numeric"):
        validate_labour_data(df)


def test_validate_labour_data_rejects_out_of_range_percentages():
    df = valid_labour_df()
    df.loc[0, "Unemployment (%)"] = 101
    with pytest.raises(DataValidationError, match="between 0 and 100"):
        validate_labour_data(df)


def test_validate_labour_data_does_not_mutate_input():
    original = valid_labour_df()
    before = original.copy(deep=True)
    validate_labour_data(original)
    pd.testing.assert_frame_equal(original, before)


def test_calculate_change_returns_last_minus_first():
    assert calculate_change(pd.Series([49.4, 49.2, 50.0])) == pytest.approx(0.6)


def test_calculate_change_ignores_missing_values():
    assert calculate_change(pd.Series([49.4, None, 50.0])) == pytest.approx(0.6)


def test_calculate_change_rejects_all_missing_values():
    with pytest.raises(DataValidationError):
        calculate_change(pd.Series([None, None]))
