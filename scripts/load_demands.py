"""Load demand CSV data and POST each row to /demands."""

import argparse
import csv
from datetime import datetime
from pathlib import Path

import httpx

API_URL = "http://localhost:8000/demands"
CSV_PATH = Path(__file__).resolve().parent.parent / "transcripts" / "Demand OIR.csv"


def parse_date_dmy(value: str) -> str:
    """Convert DD-MM-YYYY to YYYY-MM-DD."""
    return datetime.strptime(value.strip(), "%d-%m-%Y").strftime("%Y-%m-%d")


def parse_date_long(value: str) -> str:
    """Convert '17 April 2026' to YYYY-MM-DD."""
    return datetime.strptime(value.strip(), "%d %B %Y").strftime("%Y-%m-%d")


def row_to_demand(row: dict) -> dict:
    """Map a CSV row to a DemandRecord payload."""
    return {
        "demand_id": int(row["SR_ID"].strip()),
        "customer_name": row["GROUP_CUSTOMER_NAME"].strip(),
        "essential_skill": row["ESSENTIAL_SKILL"].strip(),
        "location": row["DERIVED_SR_CITY"].strip(),
        "country": row["DERIVED_SR_COUNTRY"].strip(),
        "created_on": parse_date_long(row["SR_CREATED_ON"]),
        "start_date": parse_date_dmy(row["DEM_ST_DATE"]),
        "end_date": parse_date_dmy(row["DEM_END_DATE"]),
        "role_description": row["ROLE_DESCRIPTION"].strip(),
        "work_mode": row["ONS/OFF"].strip(),
        "band": row["SR_BAND"].strip(),
        "open_positions": int(row["OPEN_POS"].strip()),
        "job_description": row["JD"].strip(),
        "role_cluster": row["SR_ROLE_CLUSTER_NAME"].strip(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Load demand CSV and POST to /demands")
    parser.add_argument("-f", "--file", default=str(CSV_PATH), help="Path to the CSV file")
    parser.add_argument("-n", "--rows", type=int, default=None, help="Number of rows to process")
    args = parser.parse_args()

    csv_path = Path(args.file)

    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))

    if args.rows is not None:
        rows = rows[: args.rows]

    print(f"Processing {len(rows)} rows from {csv_path}")

    success = 0
    failed = 0

    with httpx.Client(timeout=120) as client:
        for i, row in enumerate(rows, 1):
            demand = row_to_demand(row)
            print(f"  [{i}/{len(rows)}] demand_id={demand['demand_id']} ...", end=" ")

            resp = client.post(API_URL, json=demand)
            if resp.status_code in (200, 201, 202):
                success += 1
                print("OK")
            else:
                failed += 1
                print(f"FAILED  HTTP {resp.status_code}: {resp.text[:200]}")

    print(f"\nDone. success={success}  failed={failed}")


if __name__ == "__main__":
    main()
