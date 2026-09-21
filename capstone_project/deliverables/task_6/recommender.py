"""Risk-appetite-based mutual fund recommender for Task 6."""
from pathlib import Path
import pandas as pd

RISK_MAP = {"low": "Low", "moderate": "Moderate", "high": "High"}

def recommend_funds(risk_appetite: str, performance_csv: str | Path, n: int = 3) -> pd.DataFrame:
    """Return the top n funds by Sharpe ratio within the requested risk grade."""
    grade = RISK_MAP.get(str(risk_appetite).strip().lower())
    if grade is None:
        raise ValueError("risk_appetite must be Low, Moderate, or High")
    df = pd.read_csv(performance_csv)
    required = {"amfi_code", "scheme_name", "risk_grade", "sharpe_ratio", "return_1yr_pct", "expense_ratio_pct"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    result = df.loc[df["risk_grade"].eq(grade), list(required)].copy()
    result = result.sort_values("sharpe_ratio", ascending=False).head(n).reset_index(drop=True)
    return result

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    candidates = list((project_root / "data" / "processed").glob("*07_scheme_performance*.csv"))
    if not candidates:
        candidates = list((project_root / "data" / "raw").glob("*07_scheme_performance*.csv"))
    if not candidates:
        raise FileNotFoundError("07_scheme_performance.csv not found")
    appetite = input("Risk appetite (Low/Moderate/High): ").strip()
    print(recommend_funds(appetite, candidates[0]).to_string(index=False))
