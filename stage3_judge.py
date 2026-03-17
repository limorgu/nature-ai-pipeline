import argparse
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from spec_utils import ROOT, latest_run_root, load_json, slugify, update_stage_status, write_json


DOMAIN_CONFIG = load_json(ROOT / "domain_config.json")


def judge_quote(quote: Dict, label_keywords: Dict[str, List[str]]) -> Tuple[int, str, str, float]:
    text = str(quote.get("quote", ""))
    lowered = text.lower()
    worker_match = int(quote.get("match_found", 0))
    worker_category = quote.get("category", "None")

    if worker_match == 0:
        return 0, "FAIL", "Worker Miss", 0.0

    matched_keywords = [
        kw for kw in label_keywords.get(worker_category, [])
        if kw.lower() in lowered
    ]

    if not matched_keywords:
        return 0, "FAIL", "Out of Context", 1.0

    metaphor_cues = ["like a ", "as if", "as though", "kind of", "sort of"]
    if any(cue in lowered for cue in metaphor_cues) and worker_category in {"Fauna", "Flora"}:
        return 0, "FAIL", "Metaphor Trap", 1.0

    return 1, "PASS", "Literal Description", 0.0


def build_stage3(run_root: Path, book_filter: Optional[str] = None) -> Path:
    s2_root = run_root / "S2_Worker_Extraction" / "books"
    if not s2_root.exists():
        raise FileNotFoundError("Stage 2 outputs not found. Run stage2 first.")

    stage_root = run_root / "S3_Judge_Audit"
    books_out = stage_root / "books"
    books_out.mkdir(parents=True, exist_ok=True)
    category_root = stage_root / "categories"
    category_root.mkdir(parents=True, exist_ok=True)

    label_keywords = DOMAIN_CONFIG.get("label_keywords", {})
    books_processed = 0
    total_rows = 0
    total_pass = 0
    drift_values: List[float] = []
    category_rows: Dict[str, List[Dict]] = {category: [] for category in DOMAIN_CONFIG["taxonomy"]}

    for book_dir in sorted([p for p in s2_root.iterdir() if p.is_dir()]):
        book_id = book_dir.name
        if book_filter and book_filter != book_id:
            continue

        stage2_payload = load_json(book_dir / "raw_extractions.json")
        rows = []
        fail_reasons = Counter()
        for quote in stage2_payload.get("quotes", []):
            judge_match, status, fail_reason, drift = judge_quote(quote, label_keywords)
            drift_values.append(drift)
            if status == "FAIL":
                fail_reasons[fail_reason] += 1
            else:
                total_pass += 1

            rows.append(
                {
                    "book_id": book_id,
                    "quote_id": quote.get("quote_id"),
                    "quote": quote.get("quote"),
                    "category": quote.get("category"),
                    "worker_match": quote.get("match_found"),
                    "judge_match": judge_match,
                    "status": status,
                    "fail_reason": fail_reason,
                    "binary_drift": drift,
                    "page_number": quote.get("page_number"),
                    "image_id": quote.get("image_id"),
                    "worker_model_id": quote.get("model_id"),
                    "judge_model_id": "judge_rules_v1"
                }
            )
            category = quote.get("category")
            if category in category_rows:
                category_rows[category].append(rows[-1])

        out_book_dir = books_out / book_id
        out_book_dir.mkdir(parents=True, exist_ok=True)
        csv_path = out_book_dir / "audited_results.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            if rows:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            else:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "book_id", "quote_id", "quote", "category", "worker_match", "judge_match",
                        "status", "fail_reason", "binary_drift", "page_number", "image_id",
                        "worker_model_id", "judge_model_id"
                    ]
                )
                writer.writeheader()

        summary = {
            "book_id": book_id,
            "run_id": run_root.name,
            "total_rows": len(rows),
            "pass_count": sum(1 for row in rows if row["status"] == "PASS"),
            "fail_count": sum(1 for row in rows if row["status"] == "FAIL"),
            "avg_binary_drift": round(sum(row["binary_drift"] for row in rows) / len(rows), 4) if rows else 0.0,
            "fail_reasons": dict(fail_reasons),
            "created_at": datetime.now().isoformat()
        }
        write_json(out_book_dir / "audit_summary.json", summary)

        books_processed += 1
        total_rows += len(rows)

    manifest = {
        "run_id": run_root.name,
        "domain": DOMAIN_CONFIG["domain"],
        "books_processed": books_processed,
        "total_rows": total_rows,
        "overall_avg_binary_drift": round(sum(drift_values) / len(drift_values), 4) if drift_values else 0.0,
        "created_at": datetime.now().isoformat()
    }
    write_json(stage_root / "audit_manifest.json", manifest)
    for category, rows in category_rows.items():
        cat_dir = category_root / slugify(category)
        cat_dir.mkdir(parents=True, exist_ok=True)
        csv_path = cat_dir / "audited_results.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "book_id", "quote_id", "quote", "category", "worker_match", "judge_match",
                    "status", "fail_reason", "binary_drift", "page_number", "image_id",
                    "worker_model_id", "judge_model_id"
                ]
            )
            writer.writeheader()
            if rows:
                writer.writerows(rows)
        write_json(
            cat_dir / "audit_summary.json",
            {
                "run_id": run_root.name,
                "domain": DOMAIN_CONFIG["domain"],
                "category": category,
                "total_rows": len(rows),
                "pass_count": sum(1 for row in rows if row["status"] == "PASS"),
                "fail_count": sum(1 for row in rows if row["status"] == "FAIL")
            }
        )
    update_stage_status(
        run_root,
        "S3",
        "completed",
        {
            "books_processed": books_processed,
            "total_rows": total_rows,
            "output_root": str(stage_root)
        }
    )
    return stage_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 3 judge verification and logic audit.")
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--book-id", default=None)
    args = parser.parse_args()

    run_root = Path(args.run_root) if args.run_root else latest_run_root()
    stage_root = build_stage3(run_root=run_root, book_filter=args.book_id)
    print({"status": "ok", "stage_root": str(stage_root)})


if __name__ == "__main__":
    main()
