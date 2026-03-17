import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from spec_utils import latest_run_root, load_json, slugify, update_stage_status, write_json


def read_csv_rows(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_stage5(run_root: Path, book_filter: Optional[str] = None) -> Path:
    s1_root = run_root / "S1_Librarian_Intake_OCR" / "books"
    s3_root = run_root / "S3_Judge_Audit" / "books"
    s4_root = run_root / "S4_Analytics_Relationships" / "books"
    if not s4_root.exists():
        raise FileNotFoundError("Stage 4 outputs not found. Run stage4 first.")

    stage_root = run_root / "S5_Reports_Dashboards"
    per_book_root = stage_root / "per_book"
    per_book_root.mkdir(parents=True, exist_ok=True)
    category_root = stage_root / "categories"
    category_root.mkdir(parents=True, exist_ok=True)
    error_root = stage_root / "error_analytics"
    error_root.mkdir(parents=True, exist_ok=True)
    retention_root = stage_root / "source_retention"
    retention_root.mkdir(parents=True, exist_ok=True)

    dashboard_rows = []
    category_dashboard_rows = defaultdict(list)
    error_rows = []
    error_by_reason = defaultdict(int)
    error_by_category = defaultdict(int)
    retention_rows = []
    books_processed = 0

    for book_dir in sorted([p for p in s4_root.iterdir() if p.is_dir()]):
        book_id = book_dir.name
        if book_filter and book_filter != book_id:
            continue

        meta = load_json(s1_root / book_id / "folder_metadata.json")
        audit_summary = load_json(s3_root / book_id / "audit_summary.json")
        perf = load_json(book_dir / "performance_card.json")
        rows = read_csv_rows(s3_root / book_id / "audited_results.csv")

        total_pages = int(meta.get("total_images_in_source", 0))
        processed_pages = int(meta.get("pages_processed", 0))
        remaining_pages = max(total_pages - processed_pages, 0)
        progress_pct = meta.get("completion_percentage", "0.0%")

        report_payload = {
            "book_id": book_id,
            "run_id": run_root.name,
            "progress": {
                "total_pages": total_pages,
                "processed_pages": processed_pages,
                "remaining_pages": remaining_pages,
                "completion_percentage": progress_pct
            },
            "audit": audit_summary,
            "analytics": perf,
            "created_at": datetime.now().isoformat()
        }
        out_book_dir = per_book_root / book_id
        out_book_dir.mkdir(parents=True, exist_ok=True)
        write_json(out_book_dir / "report.json", report_payload)

        fail_rows = [row for row in rows if row["status"] == "FAIL"]
        for row in fail_rows:
            fail_reason = row["fail_reason"] or "Unknown"
            category = row["category"] or "Unknown"
            error_rows.append(
                {
                    "book_id": book_id,
                    "category": category,
                    "fail_reason": fail_reason,
                    "quote_id": row["quote_id"],
                    "page_number": row["page_number"],
                    "image_id": row["image_id"],
                    "binary_drift": row["binary_drift"]
                }
            )
            error_by_reason[fail_reason] += 1
            error_by_category[category] += 1

        md_lines = [
            f"# Report - {book_id}",
            "",
            f"- Run: `{run_root.name}`",
            f"- Pages processed: `{processed_pages}/{total_pages}`",
            f"- Pages remaining: `{remaining_pages}`",
            f"- Completion: `{progress_pct}`",
            f"- Approved quotes: `{perf['book_delta']['approved_quotes']}`",
            f"- Density per 1k words: `{perf['book_delta']['density_per_1k_words']}`",
            f"- Avg binary drift: `{perf['model_comparison']['avg_binary_drift']}`",
            f"- Fail count: `{audit_summary['fail_count']}`",
            "",
            "## Category Precision",
            ""
        ]
        for category, stats in perf["categorical_breakdown"].items():
            md_lines.append(f"- `{category}`: precision `{stats['precision']}`, count `{stats['count']}`, total `{stats['total']}`")
            category_dashboard_rows[category].append(
                {
                    "book_id": book_id,
                    "precision": stats["precision"],
                    "count": stats["count"],
                    "total": stats["total"],
                    "completion_percentage": progress_pct
                }
            )
        (out_book_dir / "report.md").write_text("\n".join(md_lines), encoding="utf-8")

        dashboard_rows.append(
            {
                "book_id": book_id,
                "completion_percentage": progress_pct,
                "pages_processed": processed_pages,
                "pages_remaining": remaining_pages,
                "overall_accuracy": perf["overall_accuracy"],
                "approved_quotes": perf["book_delta"]["approved_quotes"],
                "density_per_1k_words": perf["book_delta"]["density_per_1k_words"],
                "avg_binary_drift": perf["model_comparison"]["avg_binary_drift"],
                "total_audited_rows": len(rows)
            }
        )

        ground_truth_path = run_root / "S6_Exports_GroundTruth" / "books" / book_id / "ground_truth.json"
        exported = ground_truth_path.exists()
        completion_numeric = float(str(progress_pct).replace("%", "")) if progress_pct else 0.0
        if completion_numeric >= 100.0 and exported:
            retention_status = "ARCHIVE_READY"
            retention_reason = "OCR complete and ground truth exported"
        elif completion_numeric >= 100.0:
            retention_status = "KEEP_UNTIL_EXPORT"
            retention_reason = "OCR complete but no ground truth export yet"
        else:
            retention_status = "KEEP"
            retention_reason = "OCR incomplete"
        retention_rows.append(
            {
                "book_id": book_id,
                "total_images_in_source": total_pages,
                "pages_processed": processed_pages,
                "completion_percentage": progress_pct,
                "ground_truth_exported": exported,
                "retention_status": retention_status,
                "recommended_action": "archive_original_jpgs" if retention_status == "ARCHIVE_READY" else "keep_original_jpgs",
                "reason": retention_reason
            }
        )
        books_processed += 1

    dashboard_rows = sorted(dashboard_rows, key=lambda row: row["density_per_1k_words"], reverse=True)
    with (stage_root / "leadership_dashboard.csv").open("w", newline="", encoding="utf-8") as handle:
        if dashboard_rows:
            writer = csv.DictWriter(handle, fieldnames=list(dashboard_rows[0].keys()))
            writer.writeheader()
            writer.writerows(dashboard_rows)

    md_lines = [
        "# Leadership Dashboard",
        "",
        "| Book | Completion | Remaining | Accuracy | Approved Quotes | Density / 1k | Drift |",
        "|---|---:|---:|---:|---:|---:|---:|"
    ]
    for row in dashboard_rows:
        md_lines.append(
            f"| {row['book_id']} | {row['completion_percentage']} | {row['pages_remaining']} | "
            f"{row['overall_accuracy']} | {row['approved_quotes']} | {row['density_per_1k_words']} | {row['avg_binary_drift']} |"
        )
    (stage_root / "leadership_dashboard.md").write_text("\n".join(md_lines), encoding="utf-8")
    for category, rows in category_dashboard_rows.items():
        cat_dir = category_root / slugify(category)
        cat_dir.mkdir(parents=True, exist_ok=True)
        rows = sorted(rows, key=lambda row: row["count"], reverse=True)
        with (cat_dir / "dashboard.csv").open("w", newline="", encoding="utf-8") as handle:
            if rows:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        md_lines = [
            f"# Category Dashboard - {category}",
            "",
            "| Book | Precision | Count | Total | Completion |",
            "|---|---:|---:|---:|---:|"
        ]
        for row in rows:
            md_lines.append(
                f"| {row['book_id']} | {row['precision']} | {row['count']} | {row['total']} | {row['completion_percentage']} |"
            )
        (cat_dir / "dashboard.md").write_text("\n".join(md_lines), encoding="utf-8")

    error_rows = sorted(error_rows, key=lambda row: (row["fail_reason"], row["book_id"], row["category"]))
    with (error_root / "error_dashboard.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["book_id", "category", "fail_reason", "quote_id", "page_number", "image_id", "binary_drift"]
        )
        writer.writeheader()
        if error_rows:
            writer.writerows(error_rows)

    reason_rows = [
        {"fail_reason": reason, "count": count}
        for reason, count in sorted(error_by_reason.items(), key=lambda item: (-item[1], item[0]))
    ]
    with (error_root / "error_by_reason.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["fail_reason", "count"])
        writer.writeheader()
        if reason_rows:
            writer.writerows(reason_rows)

    category_error_rows = [
        {"category": category, "count": count}
        for category, count in sorted(error_by_category.items(), key=lambda item: (-item[1], item[0]))
    ]
    with (error_root / "error_by_category.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "count"])
        writer.writeheader()
        if category_error_rows:
            writer.writerows(category_error_rows)

    error_summary = {
        "run_id": run_root.name,
        "total_failures": len(error_rows),
        "failures_by_reason": {row["fail_reason"]: row["count"] for row in reason_rows},
        "failures_by_category": {row["category"]: row["count"] for row in category_error_rows},
        "created_at": datetime.now().isoformat()
    }
    write_json(error_root / "error_summary.json", error_summary)

    md_lines = [
        "# Error Analytics",
        "",
        f"- Total failures: `{len(error_rows)}`",
        "",
        "## Failures By Reason",
        ""
    ]
    for row in reason_rows:
        md_lines.append(f"- `{row['fail_reason']}`: `{row['count']}`")
    md_lines.append("")
    md_lines.append("## Failures By Category")
    md_lines.append("")
    for row in category_error_rows:
        md_lines.append(f"- `{row['category']}`: `{row['count']}`")
    (error_root / "error_dashboard.md").write_text("\n".join(md_lines), encoding="utf-8")

    with (retention_root / "source_retention_plan.csv").open("w", newline="", encoding="utf-8") as handle:
        if retention_rows:
            writer = csv.DictWriter(handle, fieldnames=list(retention_rows[0].keys()))
            writer.writeheader()
            writer.writerows(retention_rows)
    write_json(retention_root / "source_retention_plan.json", retention_rows)
    md_lines = [
        "# Source Retention Plan",
        "",
        "| Book | Completion | Exported | Status | Recommended Action | Reason |",
        "|---|---:|---|---|---|---|"
    ]
    for row in retention_rows:
        md_lines.append(
            f"| {row['book_id']} | {row['completion_percentage']} | {row['ground_truth_exported']} | "
            f"{row['retention_status']} | {row['recommended_action']} | {row['reason']} |"
        )
    (retention_root / "source_retention_plan.md").write_text("\n".join(md_lines), encoding="utf-8")

    manifest = {
        "run_id": run_root.name,
        "books_processed": books_processed,
        "dashboard_rows": len(dashboard_rows),
        "total_failures": len(error_rows),
        "retention_rows": len(retention_rows),
        "created_at": datetime.now().isoformat()
    }
    write_json(stage_root / "reports_manifest.json", manifest)
    update_stage_status(
        run_root,
        "S5",
        "completed",
        {
            "books_processed": books_processed,
            "output_root": str(stage_root)
        }
    )
    return stage_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 5 reports and dashboards.")
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--book-id", default=None)
    args = parser.parse_args()

    run_root = Path(args.run_root) if args.run_root else latest_run_root()
    stage_root = build_stage5(run_root=run_root, book_filter=args.book_id)
    print({"status": "ok", "stage_root": str(stage_root)})


if __name__ == "__main__":
    main()
