import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from spec_utils import ROOT, latest_run_root, load_json, slugify, update_stage_status, write_json


DOMAIN_CONFIG = load_json(ROOT / "domain_config.json")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text.replace("\n", " ")).strip()


def split_units(content: str) -> List[str]:
    content = normalize_text(content)
    if not content:
        return []
    return [p.strip() for p in SENTENCE_SPLIT_RE.split(content) if p.strip()]


def classify_unit(text: str, label_keywords: Dict[str, List[str]]) -> Tuple[int, str, float]:
    lowered = text.lower()
    scores: Dict[str, int] = {}
    for label, keywords in label_keywords.items():
        scores[label] = sum(1 for keyword in keywords if re.search(rf"\b{re.escape(keyword.lower())}\b", lowered))

    best_label = max(scores, key=scores.get) if scores else "None"
    best_score = scores.get(best_label, 0)
    match_found = 1 if best_score > 0 else 0
    confidence = min(1.0, round(best_score / 2.0, 3)) if match_found else 0.0
    return match_found, best_label if match_found else "None", confidence


def quote_id(book_id: str, page_number: Optional[int], quote: str, model_id: str) -> str:
    raw = f"{book_id}|{page_number}|{quote}|{model_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def build_stage2(run_root: Path, book_filter: Optional[str] = None) -> Path:
    s1_root = run_root / "S1_Librarian_Intake_OCR" / "books"
    if not s1_root.exists():
        raise FileNotFoundError("Stage 1 outputs not found. Run stage1 first.")

    stage_root = run_root / "S2_Worker_Extraction"
    books_out = stage_root / "books"
    books_out.mkdir(parents=True, exist_ok=True)
    category_root = stage_root / "categories"
    category_root.mkdir(parents=True, exist_ok=True)

    label_keywords = DOMAIN_CONFIG.get("label_keywords", {})
    model_id = "worker_rules_v1"
    processed_books = 0
    total_quotes = 0
    category_rows: Dict[str, List[Dict]] = {category: [] for category in DOMAIN_CONFIG["taxonomy"]}

    for book_dir in sorted([p for p in s1_root.iterdir() if p.is_dir()]):
        book_id = book_dir.name
        if book_filter and book_filter != book_id:
            continue

        pages_dir = book_dir / "pages"
        if not pages_dir.exists():
            continue

        quotes = []
        for page_json in sorted(pages_dir.glob("page_*.json")):
            page = load_json(page_json)
            page_number = page.get("page_number")
            content = page.get("content", "")
            for sentence in split_units(content):
                match_found, category, confidence = classify_unit(sentence, label_keywords)
                if match_found == 0:
                    continue
                quotes.append(
                    {
                        "quote_id": quote_id(book_id, page_number, sentence, model_id),
                        "quote": sentence,
                        "category": category,
                        "match_found": match_found,
                        "confidence": confidence,
                        "page_number": page_number,
                        "image_id": page.get("source_image"),
                        "model_id": model_id,
                        "source_file": str(page_json)
                    }
                )
                category_rows.setdefault(category, []).append(quotes[-1])

        out_book_dir = books_out / book_id
        out_book_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "book_id": book_id,
            "domain": DOMAIN_CONFIG["domain"],
            "taxonomy": DOMAIN_CONFIG["taxonomy"],
            "total_quotes": len(quotes),
            "quotes": quotes,
            "created_at": datetime.now().isoformat()
        }
        write_json(out_book_dir / "raw_extractions.json", payload)
        processed_books += 1
        total_quotes += len(quotes)

    summary = {
        "run_id": run_root.name,
        "domain": DOMAIN_CONFIG["domain"],
        "books_processed": processed_books,
        "total_quotes": total_quotes,
        "created_at": datetime.now().isoformat()
    }
    write_json(stage_root / "worker_manifest.json", summary)
    for category, rows in category_rows.items():
        cat_dir = category_root / slugify(category)
        cat_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            cat_dir / "raw_extractions.json",
            {
                "run_id": run_root.name,
                "domain": DOMAIN_CONFIG["domain"],
                "category": category,
                "total_quotes": len(rows),
                "quotes": rows
            }
        )
    update_stage_status(
        run_root,
        "S2",
        "completed",
        {
            "books_processed": processed_books,
            "total_quotes": total_quotes,
            "output_root": str(stage_root)
        }
    )
    return stage_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 2 worker extraction from Stage 1 text JSON files.")
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--book-id", default=None)
    args = parser.parse_args()

    run_root = Path(args.run_root) if args.run_root else latest_run_root()
    stage_root = build_stage2(run_root=run_root, book_filter=args.book_id)
    print(json.dumps({"status": "ok", "stage_root": str(stage_root)}, indent=2))


if __name__ == "__main__":
    main()
