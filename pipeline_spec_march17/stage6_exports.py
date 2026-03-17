import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from spec_utils import latest_run_root, load_json, slugify, update_stage_status, write_json


def read_csv_rows(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_stage6(run_root: Path, book_filter: Optional[str] = None) -> Path:
    s2_root = run_root / "S2_Worker_Extraction" / "books"
    s3_root = run_root / "S3_Judge_Audit" / "books"
    if not s3_root.exists():
        raise FileNotFoundError("Stage 3 outputs not found. Run stage3 first.")

    stage_root = run_root / "S6_Exports_GroundTruth"
    books_out = stage_root / "books"
    books_out.mkdir(parents=True, exist_ok=True)
    category_root = stage_root / "categories"
    category_root.mkdir(parents=True, exist_ok=True)

    books_processed = 0
    total_exported = 0
    category_rows = {}

    for audit_dir in sorted([p for p in s3_root.iterdir() if p.is_dir()]):
        book_id = audit_dir.name
        if book_filter and book_filter != book_id:
            continue

        stage2_payload = load_json(s2_root / book_id / "raw_extractions.json")
        quotes_by_id = {quote["quote_id"]: quote for quote in stage2_payload.get("quotes", [])}
        audit_rows = read_csv_rows(audit_dir / "audited_results.csv")

        gold_rows = []
        for row in audit_rows:
            if row["status"] != "PASS":
                continue
            quote = quotes_by_id.get(row["quote_id"])
            if not quote:
                continue
            gold_rows.append(
                {
                    "book_id": book_id,
                    "quote_id": quote["quote_id"],
                    "quote": quote["quote"],
                    "category": quote["category"],
                    "match_found": quote["match_found"],
                    "confidence": quote["confidence"],
                    "page_number": quote["page_number"],
                    "image_id": quote["image_id"],
                    "worker_model_id": quote["model_id"],
                    "judge_model_id": row["judge_model_id"],
                    "audit_status": row["status"],
                    "run_id": run_root.name
                }
            )
            category_rows.setdefault(quote["category"], []).append(gold_rows[-1])

        out_book_dir = books_out / book_id
        out_book_dir.mkdir(parents=True, exist_ok=True)
        write_json(out_book_dir / "ground_truth.json", {"book_id": book_id, "quotes": gold_rows, "total_quotes": len(gold_rows)})
        with (out_book_dir / "ground_truth.csv").open("w", newline="", encoding="utf-8") as handle:
            if gold_rows:
                writer = csv.DictWriter(handle, fieldnames=list(gold_rows[0].keys()))
                writer.writeheader()
                writer.writerows(gold_rows)

        export_manifest = {
            "book_id": book_id,
            "run_id": run_root.name,
            "exported_quotes": len(gold_rows),
            "source_stage2": str(s2_root / book_id / "raw_extractions.json"),
            "source_stage3": str(audit_dir / "audited_results.csv"),
            "created_at": datetime.now().isoformat()
        }
        write_json(out_book_dir / "export_manifest.json", export_manifest)
        books_processed += 1
        total_exported += len(gold_rows)

    manifest = {
        "run_id": run_root.name,
        "books_processed": books_processed,
        "total_exported_quotes": total_exported,
        "created_at": datetime.now().isoformat()
    }
    write_json(stage_root / "exports_manifest.json", manifest)
    for category, rows in category_rows.items():
        cat_dir = category_root / slugify(category)
        cat_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            cat_dir / "ground_truth.json",
            {
                "run_id": run_root.name,
                "category": category,
                "total_quotes": len(rows),
                "quotes": rows
            }
        )
    update_stage_status(
        run_root,
        "S6",
        "completed",
        {
            "books_processed": books_processed,
            "total_exported_quotes": total_exported,
            "output_root": str(stage_root)
        }
    )
    return stage_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 6 ground truth export.")
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--book-id", default=None)
    args = parser.parse_args()

    run_root = Path(args.run_root) if args.run_root else latest_run_root()
    stage_root = build_stage6(run_root=run_root, book_filter=args.book_id)
    print({"status": "ok", "stage_root": str(stage_root)})


if __name__ == "__main__":
    main()
