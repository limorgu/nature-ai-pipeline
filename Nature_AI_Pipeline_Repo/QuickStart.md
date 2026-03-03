## 🟢 Environment Activation
Before running any script, activate the environment:
`source /Users/limorkissos/Documents/books/inbox_photos/.feb19env/bin/activate`

---

## 🛠 The 3-Stage Pipeline

### Stage 1: Library Builder (Ingestion)
**Purpose:** Scans raw images from `Feb_books_test` and saves them into `Organized_Library`.
- **Command:** `python feb18_stage1_avoidduplication_extract.py`
- **Output:** `/Feb_results/Organized_Library/`

### Stage 2: Operations Center (Audit)
**Purpose:** Checks for missing pages, sequence gaps, and calculates completion percentages.
- **Command:** `python feb19_stage2_refiment_gap_analysis.py`
- **Output:** `/Feb_results/library_audit_YYYYMMDD/`

### Stage 3: Targeted Infill (Iterative)
**Purpose:** Manually completes a specific book folder or fills gaps identified in Stage 2.
- **Command:** `python stage3_infill.py`

---

## 🧹 Maintenance
- **To clean duplicates:** Run your consolidation script to merge partial folder names.
- **Missing Pages:** Refer to `2_gap_analysis_report.json` after running Stage 2.

