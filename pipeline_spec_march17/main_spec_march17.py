import argparse
import sys
from pathlib import Path
from typing import Optional

from stage0_workspace_architect import initialize_workspace
from stage1_librarian import build_stage1
from stage2_worker import build_stage2
from stage3_judge import build_stage3
from stage4_analytics import build_stage4
from stage5_reports import build_stage5
from stage6_exports import build_stage6
from stage7_benchmarking import build_stage7
from spec_utils import latest_run_root


ROOT = Path(__file__).resolve().parent


def run_stage0() -> None:
    run_root = initialize_workspace(
        project_config_path=ROOT / "project_config.json",
        domain_config_path=ROOT / "domain_config.json"
    )
    print(f"Stage 0 complete: {run_root}")


def run_stage1(book_id: Optional[str]) -> None:
    run_root = latest_run_root()
    stage_root = build_stage1(run_root=run_root, book_filter=book_id)
    print(f"Stage 1 complete: {stage_root}")


def run_stage2(book_id: Optional[str]) -> None:
    run_root = latest_run_root()
    stage_root = build_stage2(run_root=run_root, book_filter=book_id)
    print(f"Stage 2 complete: {stage_root}")


def run_stage3(book_id: Optional[str]) -> None:
    run_root = latest_run_root()
    stage_root = build_stage3(run_root=run_root, book_filter=book_id)
    print(f"Stage 3 complete: {stage_root}")


def run_stage4(book_id: Optional[str]) -> None:
    run_root = latest_run_root()
    stage_root = build_stage4(run_root=run_root, book_filter=book_id)
    print(f"Stage 4 complete: {stage_root}")


def run_stage5(book_id: Optional[str]) -> None:
    run_root = latest_run_root()
    stage_root = build_stage5(run_root=run_root, book_filter=book_id)
    print(f"Stage 5 complete: {stage_root}")


def run_stage6(book_id: Optional[str]) -> None:
    run_root = latest_run_root()
    stage_root = build_stage6(run_root=run_root, book_filter=book_id)
    print(f"Stage 6 complete: {stage_root}")


def run_stage7(book_id: Optional[str]) -> None:
    run_root = latest_run_root()
    stage_root = build_stage7(run_root=run_root, book_filter=book_id)
    print(f"Stage 7 complete: {stage_root}")


def run_fill_missing_ocr() -> None:
    data_test_root = ROOT.parent / "data_test"
    sys.path.insert(0, str(data_test_root))
    import March10_stage2_3_OCR as legacy_stage23  # type: ignore
    legacy_stage23.run_librarian_pipeline()


def run_all(book_id: Optional[str], skip_stage0: bool) -> None:
    if not skip_stage0:
        run_stage0()
    run_stage1(book_id)
    run_stage2(book_id)
    run_stage3(book_id)
    run_stage4(book_id)
    run_stage5(book_id)
    run_stage6(book_id)
    run_stage7(book_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Main entrypoint for SPEC_march17.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("stage0", help="Initialize a new timestamped run workspace.")
    p1 = sub.add_parser("stage1", help="Build the searchable digital library from available OCR/full-text data.")
    p1.add_argument("--book-id", default=None)
    p2 = sub.add_parser("stage2", help="Run worker extraction over Stage 1 outputs.")
    p2.add_argument("--book-id", default=None)
    p3 = sub.add_parser("stage3", help="Run judge verification over Stage 2 outputs.")
    p3.add_argument("--book-id", default=None)
    p4 = sub.add_parser("stage4", help="Build analytics and relationship outputs from Stage 3.")
    p4.add_argument("--book-id", default=None)
    p5 = sub.add_parser("stage5", help="Build human-facing reports and dashboards.")
    p5.add_argument("--book-id", default=None)
    p6 = sub.add_parser("stage6", help="Export PASS-only ground truth with provenance.")
    p6.add_argument("--book-id", default=None)
    p7 = sub.add_parser("stage7", help="Benchmark worker output against an alternate extractor.")
    p7.add_argument("--book-id", default=None)
    sub.add_parser("fill_missing_ocr", help="Run the legacy OCR gap-filler against remaining JPG pages.")
    pall = sub.add_parser("run_all", help="Run stage0 through stage7 sequentially.")
    pall.add_argument("--book-id", default=None)
    pall.add_argument("--skip-stage0", action="store_true")
    args = parser.parse_args()

    if args.command == "stage0":
        run_stage0()
    elif args.command == "stage1":
        run_stage1(args.book_id)
    elif args.command == "stage2":
        run_stage2(args.book_id)
    elif args.command == "stage3":
        run_stage3(args.book_id)
    elif args.command == "stage4":
        run_stage4(args.book_id)
    elif args.command == "stage5":
        run_stage5(args.book_id)
    elif args.command == "stage6":
        run_stage6(args.book_id)
    elif args.command == "stage7":
        run_stage7(args.book_id)
    elif args.command == "fill_missing_ocr":
        run_fill_missing_ocr()
    elif args.command == "run_all":
        run_all(args.book_id, args.skip_stage0)


if __name__ == "__main__":
    main()
