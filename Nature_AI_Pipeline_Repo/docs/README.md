This **Master README** is designed to be your project’s "Source of Truth." It documents the exact folder structure, the logic behind each stage, and how the data flows from a raw photo to a verified nature insight.

---

# 📚 Book-to-Nature AI Research Pipeline

This project automates the extraction of nature-related imagery and themes from physical books. It uses a **Multi-Stage AI Pipeline** to digitize, audit, and verify content with high precision.

## 📂 Master Directory Structure

All project data resides in the following hierarchy:

| Folder / File | Purpose |
| --- | --- |
| `Feb_books_test/` | **The Source:** Raw `.jpg` or `.png` photos of book pages. |
| `Feb_results/Organized_Library_Source/` | **The Master Library:** Structured JSON text for every page. |
| `Feb_results/Nature_Insights/` | **The Drafts:** Potential nature quotes found by `gpt-4o-mini`. |
| `Feb_results/openai_audits/` | **The Gold Standard:** Verified and categorized quotes by `gpt-4o`. |
| `Library_Audits/` | **Audit Logs:** Historical records of missing pages and word counts. |
| `library_final_metadata.json` | **The Handshake:** The current "Map" of the library's completion status. |

---

## ⚙️ The 6-Stage Workflow

### Stage 1: Initial OCR Extraction

* **Goal:** Convert raw images into text JSON files.
* **Logic:** Uses Vision AI to transcribe text verbatim. It is **duplication-aware**; it skips any image already found in the Master Library.
* **Output:** `.../Organized_Library_Source/BookTitle_Author/page_XX.json`

### Stage 2: Gap Audit (The Brain)

* **Goal:** Identify missing pages and calculate completion percentages.
* **Logic:** Compares the number of files in the Source folder vs. the Master Library.
* **Output:** Updates `library_final_metadata.json` and sorts books by lowest progress first.

### Stage 3: Smart Fill (The Iterative Filler)

* **Goal:** Close the gaps in the library efficiently.
* **Logic:** Reads the metadata, identifies "Incomplete" books, and allows you to process a specific number of missing pages to reach 100%.
* **Priority:** Always suggests books with the least progress (like *Educated*) first.

### Stage 4: Nature Extraction (The Gatherer)

* **Goal:** Find every potential mention of nature.
* **Model:** `gpt-4o-mini` (High recall, low cost).
* **Output:** `.../Nature_Insights/BookName_nature_TIMESTAMP.json`

### Stage 5: Wise Audit (The Judge)

* **Goal:** Clean the data and remove "False Positives" (like metaphors).
* **Model:** `gpt-4o` (High reasoning, high precision).
* **Output:** `.../openai_audits/BookName_WISE_AUDIT.json`

### Stage 6: Accuracy Dashboard

* **Goal:** Measure how well the AI is performing.
* **Output:** Generates a timestamped CSV (`accuracy_check_openai_results_TIMESTAMP.csv`) showing error rates and accuracy per book.

---

## 🚀 How to Run (Daily Driver)

1. **To Digitize Books:** Run the **Master Runner (Stage 2 + 3)**. It will tell you which books are empty and let you fill them page-by-page.
2. **To Analyze Nature:** Run **Stage 4** on your completed books.
3. **To Verify Results:** Run **Stage 5** to let the "Wise Auditor" check the quotes.
4. **To See Stats:** Run **Stage 6** to get your CSV report.

---

## 🛡 Safeguards & Rules

* **No Deletion:** Scripts are "Append Only." They will never delete your Master Library JSONs.
* **Flattened Paths:** Every script is locked to the same `Organized_Library_Source` path to prevent "extra" folders from being created.
* **Handshake logic:** Stage 3 *must* have a fresh Stage 2 audit to know which pages to scan.

