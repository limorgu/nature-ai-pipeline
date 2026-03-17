# SPEC_march17 Export

Clean export workspace for the March 17 modular extraction engine rebuild.

Supporting docs:
- `PIPELINE_SPEC.md`: stage contracts and operator rules
- `domain_config.json`: active domain, taxonomy, and label keywords
- `project_config.json`: storage roots and raw source paths

## Implemented Scope

- S0: workspace initialization
- S1: intake + library build using available OCR/full-text data
- S2: worker extraction using configured taxonomy
- S3: rule-based judge audit
- S4: analytics and relationship mapping
- S5: human-facing reports, dashboards, error analytics, and retention guidance
- S6: PASS-only ground truth export
- S7: benchmark comparison against an alternate extractor

## Standard Run Flow

Run all stages:

```bash
cd /Users/limorkissos/Documents/books/inbox_photos/SPEC_march17_export
python3 main_spec_march17.py run_all
```

Run one book only:

```bash
python3 main_spec_march17.py run_all --book-id Educated_TaraWestover
```

Resume an existing run after OCR gap filling:

```bash
python3 main_spec_march17.py fill_missing_ocr
python3 main_spec_march17.py run_all --skip-stage0
```

## Stage-by-Stage Commands

```bash
python3 main_spec_march17.py stage0
python3 main_spec_march17.py stage1
python3 main_spec_march17.py stage2
python3 main_spec_march17.py stage3
python3 main_spec_march17.py stage4
python3 main_spec_march17.py stage5
python3 main_spec_march17.py stage6
python3 main_spec_march17.py stage7
```

## What To Inspect After Each Stage

S0:
- `Runs/RUN_YYYYMMDD_HHMM/run_log.json`

S1:
- `S1_Librarian_Intake_OCR/library_manifest.json`
- `S1_Librarian_Intake_OCR/books/<book_id>/folder_metadata.json`
- `S1_Librarian_Intake_OCR/books/<book_id>/pages/page_<n>.json`

S2:
- `S2_Worker_Extraction/worker_manifest.json`
- `S2_Worker_Extraction/books/<book_id>/raw_extractions.json`

S3:
- `S3_Judge_Audit/books/<book_id>/audited_results.csv`
- `S3_Judge_Audit/books/<book_id>/audit_summary.json`

S4:
- `S4_Analytics_Relationships/performance_card.json`
- `S4_Analytics_Relationships/books_dashboard.csv`

S5:
- `S5_Reports_Dashboards/leadership_dashboard.md`
- `S5_Reports_Dashboards/error_analytics/error_dashboard.csv`
- `S5_Reports_Dashboards/source_retention/source_retention_plan.csv`

S6:
- `S6_Exports_GroundTruth/books/<book_id>/ground_truth.json`

S7:
- `S7_Model_Benchmarking/books/<book_id>/benchmark_summary.json`
- `S7_Model_Benchmarking/benchmark_dashboard.csv`

## Category-Specific Output Locations

- `S2_Worker_Extraction/categories/`
- `S3_Judge_Audit/categories/`
- `S4_Analytics_Relationships/categories/`
- `S5_Reports_Dashboards/categories/`
- `S6_Exports_GroundTruth/categories/`
- `S7_Model_Benchmarking/categories/`

## Switching To A Different Domain

Edit only `domain_config.json`:
- `domain`
- `taxonomy`
- `label_keywords`

Then start a fresh run with:

```bash
python3 main_spec_march17.py stage0
```

or:

```bash
python3 main_spec_march17.py run_all
```

## Model Connector Boundary

Current extraction and judge logic are deterministic and local.

Future provider-backed implementations should be added through `model_connectors.py` so the stage output format stays stable while the backend changes:
- OpenAI worker/judge connectors
- Ollama local model connectors
- alternate benchmark connectors

## Notes

- `Runs/` is generated output and should not be committed.
- `fill_missing_ocr` expects a sibling `data_test` directory if you want to reuse the legacy OCR gap-filler locally.
