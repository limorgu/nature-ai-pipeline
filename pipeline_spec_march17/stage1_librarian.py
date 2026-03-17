import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from spec_utils import ROOT, latest_run_root, load_json, update_stage_status, write_json


PROJECT_CONFIG = load_json(ROOT / "project_config.json")
RAW_SOURCES_ROOT = Path(PROJECT_CONFIG["raw_sources_root"])
LEGACY_OCR_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results/Organized_Library_Source")

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def compact_ranges(numbers: List[int]) -> str:
    if not numbers:
        return ""
    numbers = sorted(set(numbers))
    ranges = []
    start = numbers[0]
    prev = numbers[0]
    for num in numbers[1:]:
        if num == prev + 1:
            prev = num
            continue
        ranges.append(f"{start}-{prev}" if start != prev else str(start))
        start = prev = num
    ranges.append(f"{start}-{prev}" if start != prev else str(start))
    return ", ".join(ranges)


def extract_page_number(name: str) -> Optional[int]:
    match = re.search(r"page_(\d+)\.json$", name)
    if not match:
        return None
    return int(match.group(1))


def normalize_page_payload(book_id: str, page_path: Path) -> Dict:
    raw = load_json(page_path)
    return {
        "book_id": book_id,
        "page_number": raw.get("page_number"),
        "content": raw.get("content", ""),
        "source_image": raw.get("source_image"),
        "created_at": datetime.now().isoformat(),
        "source_file": str(page_path)
    }


def build_stage1(run_root: Path, book_filter: Optional[str] = None) -> Path:
    stage_root = run_root / "S1_Librarian_Intake_OCR"
    books_out = stage_root / "books"
    books_out.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    processed_books = 0

    for raw_book_dir in sorted([p for p in RAW_SOURCES_ROOT.iterdir() if p.is_dir()]):
        book_id = raw_book_dir.name
        if book_filter and book_filter != book_id:
            continue

        raw_images = sorted([p for p in raw_book_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS])
        legacy_book_dir = LEGACY_OCR_ROOT / book_id
        page_jsons = sorted(legacy_book_dir.glob("page_*.json")) if legacy_book_dir.exists() else []
        page_numbers = [n for n in (extract_page_number(p.name) for p in page_jsons) if n is not None]

        out_book_dir = books_out / book_id
        out_pages_dir = out_book_dir / "pages"
        out_pages_dir.mkdir(parents=True, exist_ok=True)

        # Resume-safe copy/normalize of page-level OCR JSON.
        copied_count = 0
        total_words = 0
        for page_path in page_jsons:
            page_num = extract_page_number(page_path.name)
            target_name = page_path.name if page_num is not None else f"page_file_{page_path.stem}.json"
            target_path = out_pages_dir / target_name
            if target_path.exists():
                payload = load_json(target_path)
            else:
                payload = normalize_page_payload(book_id, page_path)
                write_json(target_path, payload)
                copied_count += 1
            total_words += len(str(payload.get("content", "")).split())

        total_images_in_source = len(raw_images)
        pages_processed = len(page_jsons)
        missing_count = max(total_images_in_source - pages_processed, 0)
        completion = round((pages_processed / total_images_in_source * 100.0), 1) if total_images_in_source else 0.0
        sequence_gaps = ""
        if page_numbers:
            expected = set(range(min(page_numbers), max(page_numbers) + 1))
            gaps = sorted(expected - set(page_numbers))
            sequence_gaps = compact_ranges(gaps)

        folder_metadata = {
            "book_name": book_id,
            "completion_percentage": f"{completion:.1f}%",
            "pages_processed": pages_processed,
            "total_images_in_source": total_images_in_source,
            "sequence_gaps": sequence_gaps,
            "total_word_count": total_words,
            "last_updated": datetime.now().isoformat(),
            "run_root": str(run_root)
        }
        write_json(out_book_dir / "folder_metadata.json", folder_metadata)

        manifest_rows.append(folder_metadata)
        processed_books += 1

    library_manifest = {
        "run_id": run_root.name,
        "created_at": datetime.now().isoformat(),
        "books_processed": processed_books,
        "books": manifest_rows
    }
    write_json(stage_root / "library_manifest.json", library_manifest)
    update_stage_status(
        run_root,
        "S1",
        "completed",
        {
            "books_processed": processed_books,
            "output_root": str(stage_root)
        }
    )
    return stage_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 1 librarian over raw images + existing OCR library.")
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--book-id", default=None)
    args = parser.parse_args()

    run_root = Path(args.run_root) if args.run_root else latest_run_root()
    stage_root = build_stage1(run_root=run_root, book_filter=args.book_id)
    print(json.dumps({"status": "ok", "stage_root": str(stage_root)}, indent=2))


if __name__ == "__main__":
    main()
