import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from spec_utils import ROOT, latest_run_root, load_json, slugify, update_stage_status, write_json


DOMAIN_CONFIG = load_json(ROOT / "domain_config.json")


def read_csv_rows(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_stage4(run_root: Path, book_filter: Optional[str] = None) -> Path:
    s1_root = run_root / "S1_Librarian_Intake_OCR" / "books"
    s3_root = run_root / "S3_Judge_Audit" / "books"
    if not s3_root.exists():
        raise FileNotFoundError("Stage 3 outputs not found. Run stage3 first.")

    stage_root = run_root / "S4_Analytics_Relationships"
    books_out = stage_root / "books"
    books_out.mkdir(parents=True, exist_ok=True)
    category_root = stage_root / "categories"
    category_root.mkdir(parents=True, exist_ok=True)

    dashboard_rows = []
    category_totals = defaultdict(lambda: {"pass": 0, "total": 0})
    category_book_rows = defaultdict(list)
    books_processed = 0

    for audit_book_dir in sorted([p for p in s3_root.iterdir() if p.is_dir()]):
        book_id = audit_book_dir.name
        if book_filter and book_filter != book_id:
            continue

        rows = read_csv_rows(audit_book_dir / "audited_results.csv")
        meta = load_json(s1_root / book_id / "folder_metadata.json")
        total_words = int(meta.get("total_word_count", 0))
        pass_rows = [row for row in rows if row["status"] == "PASS"]
        pass_counts = Counter(row["category"] for row in pass_rows)
        total_counts = Counter(row["category"] for row in rows)

        categorical_breakdown = {}
        for category in DOMAIN_CONFIG["taxonomy"]:
            total = total_counts.get(category, 0)
            passed = pass_counts.get(category, 0)
            precision = round((passed / total), 4) if total else 0.0
            categorical_breakdown[category] = {
                "precision": precision,
                "count": passed,
                "total": total
            }
            category_totals[category]["pass"] += passed
            category_totals[category]["total"] += total
            category_book_rows[category].append(
                {
                    "book_id": book_id,
                    "precision": precision,
                    "approved_quotes": passed,
                    "total_quotes": total,
                    "density_per_1k_words": round((passed / total_words) * 1000, 4) if total_words else 0.0
                }
            )

        quote_count = len(pass_rows)
        density_per_1k = round((quote_count / total_words) * 1000, 4) if total_words else 0.0

        # Simple relationship mapping: pair counts of categories appearing on same page.
        by_page = defaultdict(set)
        for row in pass_rows:
            by_page[row["page_number"]].add(row["category"])
        relationships = Counter()
        for cats in by_page.values():
            ordered = sorted(cats)
            if len(ordered) < 2:
                continue
            for idx in range(len(ordered)):
                for jdx in range(idx + 1, len(ordered)):
                    relationships[f"{ordered[idx]}__{ordered[jdx]}"] += 1

        performance_card = {
            "book_id": book_id,
            "run_id": run_root.name,
            "overall_accuracy": round((len(pass_rows) / len(rows)), 4) if rows else 0.0,
            "categorical_breakdown": categorical_breakdown,
            "model_comparison": {
                "worker_model": "worker_rules_v1",
                "judge_model": "judge_rules_v1",
                "avg_binary_drift": round(sum(float(row["binary_drift"]) for row in rows) / len(rows), 4) if rows else 0.0
            },
            "book_delta": {
                "approved_quotes": quote_count,
                "density_per_1k_words": density_per_1k,
                "total_words": total_words
            },
            "relationship_map": dict(relationships),
            "created_at": datetime.now().isoformat()
        }

        out_book_dir = books_out / book_id
        out_book_dir.mkdir(parents=True, exist_ok=True)
        write_json(out_book_dir / "performance_card.json", performance_card)

        dashboard_rows.append(
            {
                "book_id": book_id,
                "overall_accuracy": performance_card["overall_accuracy"],
                "approved_quotes": quote_count,
                "density_per_1k_words": density_per_1k,
                "avg_binary_drift": performance_card["model_comparison"]["avg_binary_drift"],
                "total_words": total_words
            }
        )
        books_processed += 1

    overall_breakdown = {}
    for category, counts in category_totals.items():
        overall_breakdown[category] = {
            "precision": round(counts["pass"] / counts["total"], 4) if counts["total"] else 0.0,
            "count": counts["pass"],
            "total": counts["total"]
        }

    dashboard_rows = sorted(dashboard_rows, key=lambda row: row["density_per_1k_words"], reverse=True)
    with (stage_root / "books_dashboard.csv").open("w", newline="", encoding="utf-8") as handle:
        if dashboard_rows:
            writer = csv.DictWriter(handle, fieldnames=list(dashboard_rows[0].keys()))
            writer.writeheader()
            writer.writerows(dashboard_rows)

    library_card = {
        "run_id": run_root.name,
        "domain": DOMAIN_CONFIG["domain"],
        "books_processed": books_processed,
        "categorical_breakdown": overall_breakdown,
        "book_comparison": dashboard_rows,
        "created_at": datetime.now().isoformat()
    }
    write_json(stage_root / "performance_card.json", library_card)
    for category, rows in category_book_rows.items():
        cat_dir = category_root / slugify(category)
        cat_dir.mkdir(parents=True, exist_ok=True)
        rows = sorted(rows, key=lambda row: row["density_per_1k_words"], reverse=True)
        write_json(
            cat_dir / "performance_card.json",
            {
                "run_id": run_root.name,
                "domain": DOMAIN_CONFIG["domain"],
                "category": category,
                "precision": overall_breakdown[category]["precision"],
                "count": overall_breakdown[category]["count"],
                "total": overall_breakdown[category]["total"],
                "books": rows
            }
        )
        with (cat_dir / "books_dashboard.csv").open("w", newline="", encoding="utf-8") as handle:
            if rows:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
    update_stage_status(
        run_root,
        "S4",
        "completed",
        {
            "books_processed": books_processed,
            "output_root": str(stage_root)
        }
    )
    return stage_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 4 analytics and relationship mapping.")
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--book-id", default=None)
    args = parser.parse_args()

    run_root = Path(args.run_root) if args.run_root else latest_run_root()
    stage_root = build_stage4(run_root=run_root, book_filter=args.book_id)
    print({"status": "ok", "stage_root": str(stage_root)})


if __name__ == "__main__":
    main()
