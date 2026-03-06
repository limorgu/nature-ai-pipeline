
---

# 🚀 QuickStart Guide: Thematic Research AI Pipeline

Follow these steps to move from a "pile of raw photos" to a "verified, structured insight database." This guide uses **Nature Extraction** as the primary example, but the steps apply to any thematic research goal.

## 🛠 Prerequisites

1. **OpenAI API Key:** Ensure your environment has your `OPENAI_API_KEY` set.
2. **Photo Prep:** Place your source photos in a folder inside `Source_Data/`.
* **Naming Convention:** `Title_Author` (e.g., `Educated_TaraWestover`).


3. **Folder Check:** Run `stage_0_validator.py` to ensure your naming is machine-readable.

---

## 🏃‍♂️ Step 1: Digitize the Source (The Master Runner)

This is your "Daily Driver." Use this script to turn physical images into a 1:1 digital text library.

* **Action:** Run `master_runner_2_3.py`.
* **What it does:** 1. Scans your library to identify gaps (missing pages).
2. Shows a **Priority List** (Sources with 0% progress at the top).
3. Prompts you to select a source and the number of pages to process.
* **Goal:** Reach **100% completion** for your target books.

---

## 🔍 Step 2: Thematic Extraction (The Gatherer)

Once your source is 100% digitized, it’s time to find your specific research themes.

* **Action:** Run `stage_4_thematic_extraction.py`.
* **Logic:** Scans the text JSONs and pulls every quote that matches your defined criteria (e.g., Nature, Medical Symptoms, Legal Clauses).
* **Result:** Creates a "Draft" file in the `Thematic_Drafts/` folder.

---

## ⚖️ Step 3: Verify the Data (The Wise Auditor)

AI can be over-enthusiastic (hallucinating metaphors as facts). This step applies high-reasoning logic to filter out noise.

* **Action:** Run `stage_5_wise_audit.py`.
* **What it does:** Uses **GPT-4o** to categorize extracts (e.g., *Animals vs. Weather* or *Literal vs. Metaphorical*) and flags errors.
* **Result:** Creates a "Gold Standard" file in the `Final_Audits/` folder.

---

## 📊 Step 4: Review Your Accuracy

Measure the reliability of the pipeline across your entire research project.

* **Action:** Run `stage_6_accuracy_dashboard.py`.
* **Result:** Prints a performance table and saves a **Timestamped CSV** in the `Final_Audits/` folder.
* *Use this to identify which sources or themes were the hardest for the AI to interpret!*

---

## 📂 Where are my files?

* **Verified Insights:** `/Final_Audits/` (Look for `_WISE_AUDIT_` files).
* **Accuracy Reports:** `/Final_Audits/accuracy_check_results_...csv`.
* **Full Digitized Library:** `/Organized_Library_Source/`.

---

## 🆘 Troubleshooting

* **"Source not found":** Ensure your folder uses an underscore (e.g., `Book_Author`) and contains no spaces.
* **"0% Progress":** Always run the **Master Runner** first to refresh the audit metadata before starting a new extraction batch.
* **"Data Leakage":** If you see extra folders, ensure your `LIBRARY_ROOT` in the script matches the path inside your `Results` folder.

---
