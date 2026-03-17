# Pipeline Spec v1.4

## Goal

Build a modular, domain-agnostic extraction engine that converts raw book page images into:

- a searchable OCR text library,
- taxonomy-based extraction outputs,
- judge-audited records,
- analytics and error reports,
- PASS-only ground truth exports,
- benchmark comparisons across models.

The pipeline must remain resumable, configurable by domain, and safe to rerun stage by stage.

## Core Design

- `domain_config.json` defines the active domain, taxonomy, and category keywords.
- `project_config.json` defines storage roots and raw source locations.
- Each run is isolated under `Runs/RUN_YYYYMMDD_HHMM/`.
- Each stage writes only to its own stage folder.
- Later stages depend only on prior stage outputs, not on in-memory state.

## Stage Contracts

### S0 Workspace Architect

Purpose:
- Create a new run folder and initialize stage skeletons.

Outputs:
- `Runs/RUN_YYYYMMDD_HHMM/`
- `run_log.json`

Required checks:
- seven stage folders exist,
- `run_log.json` records domain, taxonomy, and stage status placeholders.

### S1 Librarian Intake + OCR Library

Purpose:
- Build a structured digital library from available OCR/full-text data.
- Track coverage and sequence gaps per book.

Outputs:
- `S1_Librarian_Intake_OCR/library_manifest.json`
- `S1_Librarian_Intake_OCR/books/<book_id>/folder_metadata.json`
- `S1_Librarian_Intake_OCR/books/<book_id>/pages/page_<n>.json`

Required page fields:
- `book_id`
- `page_number`
- `content`
- `source_image`

### S2 Worker Extraction

Purpose:
- Run high-recall extraction against the configured taxonomy.

Outputs:
- `S2_Worker_Extraction/worker_manifest.json`
- `S2_Worker_Extraction/books/<book_id>/raw_extractions.json`
- `S2_Worker_Extraction/categories/<category_slug>/raw_extractions.json`

Required quote fields:
- `quote_id`
- `quote`
- `category`
- `match_found`
- `confidence`
- `page_number`
- `image_id`
- `model_id`
- `source_file`

### S3 Judge Audit

Purpose:
- Verify worker matches and flag removals with explicit fail reasons.

Outputs:
- `S3_Judge_Audit/audit_manifest.json`
- `S3_Judge_Audit/books/<book_id>/audited_results.csv`
- `S3_Judge_Audit/books/<book_id>/audit_summary.json`
- category-specific audit outputs under `S3_Judge_Audit/categories/`

Required audit fields:
- `worker_match`
- `judge_match`
- `status`
- `fail_reason`
- `binary_drift`

### S4 Analytics + Relationship Mapping

Purpose:
- Summarize performance by book and category.
- Compute density, precision, and relationship views.

Outputs:
- `S4_Analytics_Relationships/performance_card.json`
- `S4_Analytics_Relationships/books_dashboard.csv`
- per-book and per-category `performance_card.json`

Required metrics:
- `overall_accuracy`
- `avg_binary_drift`
- `quote_density_per_1k_words`
- categorical counts and precision

### S5 Reports + Dashboards

Purpose:
- Publish human-readable reports for operators and leadership.
- Publish error analytics and source retention guidance.

Outputs:
- `S5_Reports_Dashboards/leadership_dashboard.md`
- `S5_Reports_Dashboards/per_book/<book_id>/report.json`
- `S5_Reports_Dashboards/error_analytics/`
- `S5_Reports_Dashboards/source_retention/`

Error analytics outputs:
- `error_summary.json`
- `error_dashboard.csv`
- `error_dashboard.md`
- `error_by_reason.csv`
- `error_by_category.csv`

### S6 Exports + Ground Truth

Purpose:
- Export PASS-only records with provenance.

Outputs:
- `S6_Exports_GroundTruth/books/<book_id>/ground_truth.json`
- category-specific exports under `S6_Exports_GroundTruth/categories/`

Required fields:
- `quote_id`
- `quote`
- `category`
- `page_number`
- `image_id`
- `worker_model_id`
- `judge_model_id`

### S7 Model Benchmarking

Purpose:
- Compare the active worker against alternate extraction strategies.

Outputs:
- `S7_Model_Benchmarking/books/<book_id>/benchmark_summary.json`
- `S7_Model_Benchmarking/benchmark_dashboard.csv`
- category-specific benchmark outputs

Required metrics:
- `precision`
- `recall`
- `false_positive_count`
- `false_negative_count`
- `avg_binary_drift`

## Operator Runbook

Run all stages:

```bash
python3 main_spec_march17.py run_all
```

Run a single book:

```bash
python3 main_spec_march17.py run_all --book-id Educated_TaraWestover
```

Resume a current run after filling OCR gaps:

```bash
python3 main_spec_march17.py fill_missing_ocr
python3 main_spec_march17.py run_all --skip-stage0
```

## Domain Switching

To change extraction focus without changing pipeline logic:

1. Edit `domain_config.json`
2. Replace:
   - `domain`
   - `taxonomy`
   - `label_keywords`
3. Start a new run with `stage0` or `run_all`

Current implementation is rules-based. Real model backends should be swapped in through `model_connectors.py` while preserving the same stage output contracts.
