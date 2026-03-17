# nature-ai-pipeline

This branch now contains two side-by-side codebases for comparison:

- `manual_pipeline_legacy/`
- `pipeline_spec_march17/`

Comparison guide:
- `comparison_notes/legacy_vs_spec_march17.md`

### Manual pipeline

Curated snapshot of the original step-by-step implementation:
- stage scripts
- orchestrator
- config
- architecture and quickstart docs

### SPEC_march17 pipeline

Clean modular rebuild with explicit stage contracts:
- `pipeline_spec_march17/README.md`
- `pipeline_spec_march17/PIPELINE_SPEC.md`
- `pipeline_spec_march17/main_spec_march17.py`

Run the rebuilt pipeline from:

```bash
cd pipeline_spec_march17
python3 main_spec_march17.py run_all
```

This branch intentionally excludes generated book outputs and OCR/result data.
