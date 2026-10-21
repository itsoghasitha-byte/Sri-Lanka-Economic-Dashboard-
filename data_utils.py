"""CSV validation and numeric calculations for the Sri Lanka dashboard."""
import pandas as pd

REQUIRED_COLUMNS = {"Period", "Labour force participation (%)", "Unemployment (%)"}
NUMERIC_COLUMNS = ["Labour force participation (%)", "Unemployment (%)"]


class DataValidationError(ValueError):
    """Raised when uploaded CSV data cannot be safely analysed."""


def load_csv(file_obj) -> pd.DataFrame:
    """Read a CSV file-like object and reject empty or malformed datasets."""
    try:
        df = pd.read_csv(file_obj)
    except Exception as exc:
        raise DataValidationError(f"Unable to parse CSV: {exc}") from exc

    if df.empty:
        raise DataValidationError("CSV contains no data rows.")
    if len(df.columns) == 0:
        raise DataValidationError("CSV must contain at least one column.")
    if any(not str(col).strip() for col in df.columns):
        raise DataValidationError("Column names must not be blank.")
    if df.columns.duplicated().any():
        raise DataValidationError("Column names must be unique.")
    return df


def validate_labour_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate the labour indicator table; missing numeric values are rejected."""
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise DataValidationError("Missing required column(s): " + ", ".join(sorted(missing_cols)))
    if df.empty:
        raise DataValidationError("Labour dataset contains no rows.")

    result = df.copy()
    for col in NUMERIC_COLUMNS:
        result[col] = pd.to_numeric(result[col], errors="coerce")
        if result[col].isna().any():
            raise DataValidationError(f"Missing or non-numeric values in '{col}'.")
        if ((result[col] < 0) | (result[col] > 100)).any():
            raise DataValidationError(f"Values in '{col}' must be between 0 and 100.")

    if result["Period"].isna().any() or result["Period"].astype(str).str.strip().eq("").any():
        raise DataValidationError("Period values must not be missing or blank.")
    return result


def calculate_change(series: pd.Series) -> float:
    """Return last minus first value; returns 0 for a one-row series."""
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        raise DataValidationError("Cannot calculate change without numeric values.")
    return float(numeric.iloc[-1] - numeric.iloc[0])
