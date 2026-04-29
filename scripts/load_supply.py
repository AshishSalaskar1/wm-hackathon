"""Load employee CSV data and POST each row to /supply/vectorize."""

import argparse
import csv
from datetime import datetime
from pathlib import Path

import httpx

API_URL = "http://localhost:8000/supply/vectorize"
CSV_PATH = Path(__file__).resolve().parent.parent / "transcripts" / "EmpDataNew.csv"
BATCH_SIZE = 10


def parse_date(value: str) -> str:
    """Convert DD-MM-YYYY to YYYY-MM-DD for the API."""
    return datetime.strptime(value.strip(), "%d-%m-%Y").strftime("%Y-%m-%d")


def row_to_profile(row: dict) -> dict:
    """Map a CSV row to a SupplyProfile payload."""
    return {
        "employee_id": str(row["EMP_NO"]).strip(),
        "employee_name": row["EMP_NAME"].strip(),
        "band": row["BAND"].strip(),
        "availability_from": parse_date(row["NB_FROM"]),
        "ageing_bucket": row["AGEING_BUCKET"].strip(),
        "work_mode": row["ONSITE_OFFSHORE"].strip(),
        "location": row["Location"].strip(),
        "experience": row["EXPERIENCE"].strip(),
        "role_name": row["ROLE_NAME"].strip() or None,
        "country": row["COUNTRY"].strip(),
        "skills_iaspire": row["Skills_from_iAspire"].strip() or None,
        "certified_skills": row["CERTIFIED_SKILLS"].strip() or None,
        "trained_skills": row["TRAINED_SKILLS"].strip() or None,
        "recent_skills": row["RECENT_SKILL"].strip() or None,
        "language_skills": row["LANGUAGE_SKILL"].strip() or None,
        "role_cluster": row["ROLE_CLUSTER_NAME"].strip() or None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Load employee CSV and POST to /supply/vectorize")
    parser.add_argument("-f", "--file", default=str(CSV_PATH), help="Path to the CSV file")
    parser.add_argument("-s", "--start", type=int, default=0, help="Start row index (0-based, inclusive)")
    parser.add_argument("-e", "--end", type=int, default=None, help="End row index (exclusive)")
    args = parser.parse_args()

    csv_path = Path(args.file)

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    rows = rows[args.start : args.end]

    print(f"Processing {len(rows)} rows from {csv_path}")

    profiles = [row_to_profile(r) for r in rows]
    indexed = 0
    skipped = 0
    failed = 0

    with httpx.Client(timeout=120) as client:
        for i in range(0, len(profiles), BATCH_SIZE):
            batch = profiles[i : i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            print(f"  Batch {batch_num}: sending {len(batch)} profiles ...", end=" ")

            resp = client.post(API_URL, json={"profiles": batch})
            if resp.status_code == 200:
                data = resp.json()
                indexed += data["indexed"]
                skipped += data["skipped"]
                failed += data["failed"]
                print(
                    f"OK  (indexed={data['indexed']}, "
                    f"skipped={data['skipped']}, "
                    f"failed={data['failed']})"
                )
            else:
                failed += len(batch)
                print(f"FAILED  HTTP {resp.status_code}: {resp.text[:200]}")

    print(f"\nDone. indexed={indexed}  skipped={skipped}  failed={failed}")


if __name__ == "__main__":
    main()
