
import json
import pandas as pd
from pathlib import Path
import os

# Minimal ETL with no external services to keep setup fast
DATA_DIR = Path(__file__).parent / "data"
SRC = DATA_DIR / "segments.geojson"
OUT = DATA_DIR / "segments_scored.parquet"


def ingest() -> pd.DataFrame:
    with open(SRC, "r", encoding="utf-8") as f:
        gj = json.load(f)
    rows = []
    for feat in gj["features"]:
        prop = feat.get("properties", {})
        rows.append({
            "id": prop.get("id"),
            "name": prop.get("name"),
            "lighting": prop.get("lighting", "unknown"),
            "sidewalk": prop.get("sidewalk", "unknown"),
            "speed_limit": prop.get("speed_limit", 50),
        })
    return pd.DataFrame(rows)


def score(df: pd.DataFrame) -> pd.DataFrame:
    def s(row):
        base = 0.8
        if row["lighting"] == "dim":
            base -= 0.1
        if row["sidewalk"] == "narrow":
            base -= 0.15
        if row["speed_limit"] and row["speed_limit"] > 50:
            base -= 0.05
        return max(0.0, min(1.0, base))
    df["safety_score"] = df.apply(s, axis=1)
    return df


# --- Prefect wrappers (optional, enabled when Prefect is installed) ---
try:
    from prefect import flow, task

    @task
    def task_ingest() -> pd.DataFrame:
        return ingest()

    @task
    def task_score(df: pd.DataFrame) -> pd.DataFrame:
        return score(df)

    @flow(name="PathGuard ETL")
    def prefect_main():
        df = task_ingest()
        df = task_score(df)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(OUT, index=False)
        print(f"Wrote {OUT} with {len(df)} rows")
except Exception:
    flow = None  # Prefect not available; fallback to CLI main()


# Allow disabling Prefect explicitly (e.g., on Windows without CFFI)
if os.getenv("PREFECT_DISABLE", "0") == "1":
    flow = None


def main():
    df = ingest()
    df = score(df)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)
    print(f"Wrote {OUT} with {len(df)} rows")


if __name__ == "__main__":
    if flow is not None:
        try:
            prefect_main()
        except Exception as e:
            print(f"Prefect run failed ({e}); falling back to plain ETL.")
            main()
    else:
        main()
