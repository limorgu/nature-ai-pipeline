# SPEC_march17 Export

Clean export workspace for the March 17 extraction engine rebuild.

Current scope:
- Stage 0 implemented: workspace initialization
- Stage 1 implemented: intake + library build using available OCR/full-text data
- Stage 2 implemented: worker extraction using configured taxonomy
- Stage 3 implemented: rule-based judge audit
- Stage 4 implemented: analytics and relationship mapping
- Stage 5 implemented: human-facing reports and dashboards
- Stage 6 implemented: PASS-only ground truth export
- Stage 7 implemented: benchmark comparison against an alternate extractor

Run Stage 0:

```bash
cd /Users/limorkissos/Documents/books/inbox_photos/SPEC_march17
python3 main_spec_march17.py stage0
```

Run Stage 1:

```bash
python3 main_spec_march17.py stage1
```

Run Stage 2:

```bash
python3 main_spec_march17.py stage2
```

Run Stage 3:

```bash
python3 main_spec_march17.py stage3
```

Run Stage 4:

```bash
python3 main_spec_march17.py stage4
```

Run Stage 5:

```bash
python3 main_spec_march17.py stage5
```

Run Stage 6:

```bash
python3 main_spec_march17.py stage6
```

Run Stage 7:

```bash
python3 main_spec_march17.py stage7
```

Run the full pipeline:

```bash
python3 main_spec_march17.py run_all
```

Run the full pipeline for one book:

```bash
python3 main_spec_march17.py run_all --book-id Educated_TaraWestover
```

Fill missing OCR pages first, then continue on the current run:

```bash
python3 main_spec_march17.py fill_missing_ocr
python3 main_spec_march17.py run_all --skip-stage0
```

To switch to a different domain or category set:
- edit `domain_config.json`
- update `taxonomy` and `label_keywords`
- run a new pipeline with `stage0` or `run_all`

Category-specific outputs are written under:
- `S2_Worker_Extraction/categories/`
- `S3_Judge_Audit/categories/`
- `S4_Analytics_Relationships/categories/`
- `S5_Reports_Dashboards/categories/`
- `S6_Exports_GroundTruth/categories/`
- `S7_Model_Benchmarking/categories/`

Source retention guidance is written under:
- `S5_Reports_Dashboards/source_retention/`

Notes:
- `Runs/` is generated output and should not be committed.
- `fill_missing_ocr` expects a sibling `data_test` directory if you want to reuse the legacy OCR gap-filler locally.
