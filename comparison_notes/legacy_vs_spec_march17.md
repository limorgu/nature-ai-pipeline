# Legacy vs SPEC_march17

## Purpose

This repository now contains two parallel pipeline implementations for comparison:

- `manual_pipeline_legacy/`: the manually built step-by-step pipeline
- `pipeline_spec_march17/`: the rebuilt modular pipeline

The intent is to compare architecture, stage boundaries, output contracts, and operator flow without mixing generated data into Git.

## Directory Map

### Manual Pipeline

- `manual_pipeline_legacy/MAIN_PIPELINE.py`
- `manual_pipeline_legacy/pipeline_config.py`
- `manual_pipeline_legacy/March10_stage0_Sanitization.py`
- `manual_pipeline_legacy/March10_stage2_3_OCR.py`
- `manual_pipeline_legacy/Stage3_5_Metadata.py`
- `manual_pipeline_legacy/March10_stage4_Extraction.py`
- `manual_pipeline_legacy/March10_stage5_Audit.py`
- `manual_pipeline_legacy/March10_stage6_comparemodels.py`
- `manual_pipeline_legacy/March9_stage_7_benchmark.py`

### Rebuilt Pipeline

- `pipeline_spec_march17/main_spec_march17.py`
- `pipeline_spec_march17/project_config.json`
- `pipeline_spec_march17/domain_config.json`
- `pipeline_spec_march17/stage0_workspace_architect.py`
- `pipeline_spec_march17/stage1_librarian.py`
- `pipeline_spec_march17/stage2_worker.py`
- `pipeline_spec_march17/stage3_judge.py`
- `pipeline_spec_march17/stage4_analytics.py`
- `pipeline_spec_march17/stage5_reports.py`
- `pipeline_spec_march17/stage6_exports.py`
- `pipeline_spec_march17/stage7_benchmarking.py`

## Stage Mapping

| Legacy | SPEC_march17 | Main difference |
|---|---|---|
| `March10_stage0_Sanitization.py` | `stage0_workspace_architect.py` | Legacy cleans and verifies existing folders. New pipeline creates isolated run workspaces. |
| `March10_stage2_3_OCR.py` | `stage1_librarian.py` | Legacy performs OCR + gap audit directly. New pipeline structures intake outputs per run and can bridge to legacy OCR. |
| `Stage3_5_Metadata.py` | `stage1_librarian.py` and `stage4_analytics.py` | Legacy metadata is a separate aggregation step. New pipeline carries structured metadata forward into later analytics. |
| `March10_stage4_Extraction.py` | `stage2_worker.py` | Legacy uses direct model calls with one topic and model from config. New pipeline uses a domain config and stable output contracts. |
| `March10_stage5_Audit.py` | `stage3_judge.py` and `stage5_reports.py` | Legacy audit and summary are coupled. New pipeline separates line audit from reporting. |
| `March10_stage6_comparemodels.py` | `stage7_benchmarking.py` | Legacy comparison is summary-table oriented. New pipeline ties benchmark outputs to PASS-only ground truth. |
| `March9_stage_7_benchmark.py` | `stage7_benchmarking.py` | Legacy benchmarks local models directly on sample pages. New pipeline benchmarks against the stage outputs and contracts. |

## Design Differences

### Manual Pipeline Strengths

- Real model routing already exists for OpenAI, DeepSeek, and Ollama.
- Practical output folders were built around the actual dataset and working habits.
- OCR and extraction were developed directly against real book data.

### Manual Pipeline Limitations

- Strong dependency on fixed local paths.
- Stage boundaries are less strict.
- Output contracts are less consistent across stages.
- Progress and run isolation are weaker.

### SPEC_march17 Strengths

- Clean run isolation under `Runs/`.
- Domain-agnostic configuration through `domain_config.json`.
- Stable stage contracts and category-specific outputs.
- Built-in dashboards, error analytics, retention guidance, and ground truth export boundaries.

### SPEC_march17 Limitations

- Current worker and judge are mostly rules-based placeholders.
- Legacy OCR still needs to be bridged for real JPG ingestion.
- Real provider-backed connectors are not yet wired into stage execution.

## Recommended Comparison Order

1. Compare the orchestrators:
   - `manual_pipeline_legacy/MAIN_PIPELINE.py`
   - `pipeline_spec_march17/main_spec_march17.py`
2. Compare configuration models:
   - `manual_pipeline_legacy/pipeline_config.py`
   - `pipeline_spec_march17/project_config.json`
   - `pipeline_spec_march17/domain_config.json`
3. Compare extraction and audit stages:
   - `manual_pipeline_legacy/March10_stage4_Extraction.py`
   - `pipeline_spec_march17/stage2_worker.py`
   - `manual_pipeline_legacy/March10_stage5_Audit.py`
   - `pipeline_spec_march17/stage3_judge.py`
4. Compare reporting and benchmarking:
   - `manual_pipeline_legacy/March10_stage6_comparemodels.py`
   - `manual_pipeline_legacy/March9_stage_7_benchmark.py`
   - `pipeline_spec_march17/stage5_reports.py`
   - `pipeline_spec_march17/stage7_benchmarking.py`

## What Is Intentionally Excluded

This comparison branch excludes:

- OCR result libraries
- extracted book JSON outputs
- dashboards generated from real runs
- model binaries
- book photos

Only code and documentation are included so the branch stays safe to review and merge.
