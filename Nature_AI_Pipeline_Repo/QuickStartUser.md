
---

# 🚀 QuickStart Guide: Nature AI Research

Follow these steps to move a physical book from a "pile of photos" to a "verified nature database."

## 🛠 Prerequisites

1. **OpenAI API Key:** Ensure your environment has `OPENAI_API_KEY` set.
2. **Photo Prep:** Place your book photos in a folder inside `Feb_books_test/`.
* *Naming Convention:* `Title_Author` (e.g., `Educated_TaraWestover`).



---

## 🏃‍♂️ Step 1: Digitize the Books (The Master Runner)

This is your "Daily Driver." Use this script to turn images into searchable text.

* **Action:** Run `master_runner_2_3.py`.
* **What it does:** 1.  Scans your library to see what is missing.
2.  Shows you a **Priority List** (Books with 0% progress at the top).
3.  Asks: *"Select book number to process."*
4.  Asks: *"How many pages to fill?"*
* **Goal:** Get your target books to **100% completion**.

---

## 🌿 Step 2: Extract Nature Quotes (The Gatherer)

Once a book is 100% digitized, it’s time to find the nature imagery.

* **Action:** Run `stage_4_nature_extraction.py`.
* **What it does:** Scans the text JSONs and pulls every quote that mentions animals, weather, or landscapes.
* **Result:** Creates a "Draft" file in `Feb_results/Nature_Insights/`.

---

## ⚖️ Step 3: Verify the Data (The Wise Auditor)

AI can sometimes be too enthusiastic. This step filters out metaphors (e.g., "he had a stormy personality") to keep only literal nature.

* **Action:** Run `stage_5_wise_audit.py`.
* **What it does:** Uses a high-reasoning model (GPT-4o) to categorize quotes into *Animals, Weather, Places, etc.* and flags errors.
* **Result:** Creates a "Gold Standard" file in `Feb_results/openai_audits/`.

---

## 📊 Step 4: Review Your Accuracy

See how well the pipeline performed across your entire library.

* **Action:** Run `stage_6_accuracy_dashboard.py`.
* **Result:** Prints a table to your screen and saves a **Timestamped CSV** in the `openai_audits/` folder.
* *Check this file to see which books were the hardest for the AI to understand!*



---

## 📂 Where are my files?

* **Verified Results:** `/Feb_results/openai_audits/` (Look for `_WISE_AUDIT_` files).
* **Accuracy Report:** `/Feb_results/openai_audits/accuracy_check_openai_results_...csv`.
* **Full Book Text:** `/Feb_results/Organized_Library_Source/`.

---

## 🆘 Troubleshooting

* **"Book not found":** Ensure your folder in `Feb_books_test` uses an underscore (e.g., `Book_Author`).
* **"0% Progress":** Always run the **Master Runner** first to refresh the audit before starting a new batch.
* **"Extra Folders":** If you see a second `Organized_Library_Source` folder, delete the empty one and ensure all scripts are using the path inside `Feb_results`.
