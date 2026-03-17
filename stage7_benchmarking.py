import argparse
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from spec_utils import ROOT, latest_run_root, load_json, slugify, update_stage_status, write_json


DOMAIN_CONFIG = load_json(ROOT / "domain_config.json")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def split_units(content: str) -> List[str]:
    content = normalize_text(content)
    if not content:
        return []
    return [p.strip() for p in SENTENCE_SPLIT_RE.split(content) if p.strip()]


def alt_model_match(text: str, label_keywords: Dict[str, List[str]]) -> Optional[str]:
    lowered = text.lower()
    # More permissive than worker: substring-ish stems for quick benchmark contrast.
    for label, keywords in label_keywords.items():
        for keyword in keywords:
            stem = keyword.lower()[:4]
            if stem and stem in lowered:
                return label
    return None


def quote_key(text: str) -> str:
    return re.sub(r"\W+", "", text.lower())


def build_stage7(run_root: Path, book_filter: Optional[str] = None) -> Path:
    s1_root = run_root / "S1_Librarian_Intake_OCR" / "books"
    s2_root = run_root / "S2_Worker_Extraction" / "books"
    s6_root = run_root / "S6_Exports_GroundTruth" / "books"
    if not s6_root.exists():
        raise FileNotFoundError("Stage 6 outputs not found. Run stage6 first.")

    stage_root = run_root / "S7_Model_Benchmarking"
    books_out = stage_root / "books"
    books_out.mkdir(parents=True, exist_ok=True)
    category_root = stage_root / "categories"
    category_root.mkdir(parents=True, exist_ok=True)

    label_keywords = DOMAIN_CONFIG.get("label_keywords", {})
    dashboard_rows = []
    category_dashboard = defaultdict(list)
    books_processed = 0

    for book_dir in sorted([p for p in s1_root.iterdir() if p.is_dir()]):
        book_id = book_dir.name
        if book_filter and book_filter != book_id:
            continue

        worker_payload = load_json(s2_root / book_id / "raw_extractions.json")
        gold_payload = load_json(s6_root / book_id / "ground_truth.json")
        gold_set: Set[str] = {quote_key(row["quote"]) for row in gold_payload.get("quotes", [])}

        worker_set: Set[str] = {quote_key(row["quote"]) for row in worker_payload.get("quotes", [])}

        alt_predictions = []
        pages_dir = book_dir / "pages"
        for page_json in sorted(pages_dir.glob("page_*.json")):
            page = load_json(page_json)
            for sentence in split_units(page.get("content", "")):
                category = alt_model_match(sentence, label_keywords)
                if category:
                    alt_predictions.append({"quote": sentence, "category": category})
        alt_set: Set[str] = {quote_key(row["quote"]) for row in alt_predictions}

        def score(pred_set: Set[str], gold: Set[str]) -> Dict[str, float]:
            tp = len(pred_set & gold)
            pred = len(pred_set)
            gold_n = len(gold)
            precision = round(tp / pred, 4) if pred else 0.0
            recall = round(tp / gold_n, 4) if gold_n else 0.0
            f1 = round((2 * precision * recall) / (precision + recall), 4) if (precision + recall) else 0.0
            return {"tp": tp, "predictions": pred, "gold": gold_n, "precision": precision, "recall": recall, "f1": f1}

        worker_score = score(worker_set, gold_set)
        alt_score = score(alt_set, gold_set)

        benchmark_payload = {
            "book_id": book_id,
            "run_id": run_root.name,
            "reference_model": "judge_rules_v1_ground_truth",
            "models": {
                "worker_rules_v1": worker_score,
                "benchmark_alt_rules_v1": alt_score
            },
            "winner_by_f1": "worker_rules_v1" if worker_score["f1"] >= alt_score["f1"] else "benchmark_alt_rules_v1",
            "created_at": datetime.now().isoformat()
        }
        out_book_dir = books_out / book_id
        out_book_dir.mkdir(parents=True, exist_ok=True)
        write_json(out_book_dir / "benchmark_summary.json", benchmark_payload)
        for category in DOMAIN_CONFIG["taxonomy"]:
            worker_cat = {
                quote_key(row["quote"])
                for row in worker_payload.get("quotes", [])
                if row.get("category") == category
            }
            gold_cat = {
                quote_key(row["quote"])
                for row in gold_payload.get("quotes", [])
                if row.get("category") == category
            }
            alt_cat = {
                quote_key(row["quote"])
                for row in alt_predictions
                if row.get("category") == category
            }
            def score(pred_set: Set[str], gold: Set[str]) -> Dict[str, float]:
                tp = len(pred_set & gold)
                pred = len(pred_set)
                gold_n = len(gold)
                precision = round(tp / pred, 4) if pred else 0.0
                recall = round(tp / gold_n, 4) if gold_n else 0.0
                f1 = round((2 * precision * recall) / (precision + recall), 4) if (precision + recall) else 0.0
                return {"tp": tp, "predictions": pred, "gold": gold_n, "precision": precision, "recall": recall, "f1": f1}
            worker_cat_score = score(worker_cat, gold_cat)
            alt_cat_score = score(alt_cat, gold_cat)
            category_dashboard[category].append(
                {
                    "book_id": book_id,
                    "worker_f1": worker_cat_score["f1"],
                    "alt_f1": alt_cat_score["f1"],
                    "winner_by_f1": "worker_rules_v1" if worker_cat_score["f1"] >= alt_cat_score["f1"] else "benchmark_alt_rules_v1"
                }
            )

        dashboard_rows.append(
            {
                "book_id": book_id,
                "worker_precision": worker_score["precision"],
                "worker_recall": worker_score["recall"],
                "worker_f1": worker_score["f1"],
                "alt_precision": alt_score["precision"],
                "alt_recall": alt_score["recall"],
                "alt_f1": alt_score["f1"],
                "winner_by_f1": benchmark_payload["winner_by_f1"]
            }
        )
        books_processed += 1

    with (stage_root / "benchmark_dashboard.csv").open("w", newline="", encoding="utf-8") as handle:
        if dashboard_rows:
            writer = csv.DictWriter(handle, fieldnames=list(dashboard_rows[0].keys()))
            writer.writeheader()
            writer.writerows(dashboard_rows)

    wins = Counter(row["winner_by_f1"] for row in dashboard_rows)
    manifest = {
        "run_id": run_root.name,
        "books_processed": books_processed,
        "wins_by_model": dict(wins),
        "created_at": datetime.now().isoformat()
    }
    write_json(stage_root / "benchmark_manifest.json", manifest)
    for category, rows in category_dashboard.items():
        cat_dir = category_root / slugify(category)
        cat_dir.mkdir(parents=True, exist_ok=True)
        with (cat_dir / "benchmark_dashboard.csv").open("w", newline="", encoding="utf-8") as handle:
            if rows:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
    update_stage_status(
        run_root,
        "S7",
        "completed",
        {
            "books_processed": books_processed,
            "output_root": str(stage_root)
        }
    )
    return stage_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 7 model benchmarking.")
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--book-id", default=None)
    args = parser.parse_args()

    run_root = Path(args.run_root) if args.run_root else latest_run_root()
    stage_root = build_stage7(run_root=run_root, book_filter=args.book_id)
    print({"status": "ok", "stage_root": str(stage_root)})


if __name__ == "__main__":
    main()
