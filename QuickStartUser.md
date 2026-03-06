



---

# 🚀 QuickStart Guide: Nature AI Research Pipeline

Follow these steps to move from a "pile of raw photos" to a **"Gold Standard"** insight database.

## 🛠 Prerequisites

1. **OpenAI API Key:** Ensure your environment has `OPENAI_API_KEY` set.
2. **Photo Prep:** Place your source photos in `Feb_books_test/`.
* **Naming Convention:** `Title_Author` (No spaces, use underscores).


3. **The Orchestrator:** Launch the mission control:
```bash
python main.py

```



---

## 🏃‍♂️ Phase A: Digitization (The Foundation)

Before you can analyze nature, you must create a **1:1 Digital Twin** of your books.

* **Action:** Select **Option [1]** in the menu.
* **What it does:** Runs the **Librarian (Stages 1-3)**. It transcribes images and audits gaps until your library reaches **100.0% completion**.
* **Goal:** Populate `Organized_Library_Source/` with verbatim JSON text.

---

## 🌿 Phase B: Research (Thematic Extraction)

Once your library is digitized, run the thematic extraction sequence.

* **Action:** Select **Option [2]** in the menu.
* **What it does:** Executes the **Research Pipeline (Stages 4-6)** in sequence:
1. **Gatherer (Stage 4):** Harvests every potential nature mention.
2. **Judge (Stage 5):** Uses **GPT-4o** to verify quotes and filter metaphors.
3. **Purifier (Stage 6):** Creates a "Gold Standard" file and accuracy report.


* **Result:** Creates a new timestamped "Time-Capsule" folder for your run.

---

## 📂 Where is my Data?

Your research is now organized in the **Hierarchical Hub** inside `openai_audits/`:

`.../openai_audits/[Book_Name_Timestamp]/`

* **`S4_V1/`**: Raw nature extractions.
* **`S5_V1/`**: Verified "Wise Audits".
* **`S6_Gold/`**: The purified "Gold Standard" quotes for your Substack.

---

## 🧹 Maintenance: Keeping it "Crisp"

If your workspace feels cluttered, or you have loose files from old runs:

* **Action:** Select **Option [0]** (Stage 0: Pre-flight).
* **What it does:** Automatically validates your book titles and performs an **In-Place Organization** to tuck files into their correct subfolders.

---

## 🆘 Troubleshooting

* **"Missing Stage Files":** Ensure all `March_X_stage_X.py` files are in the same folder as `main.py`.
* **"Skipping Book":** The pipeline is **Aware**. If it sees you already processed those pages in an existing timestamped folder, it will skip them to save you money.
* **"Linguistic Fog":** If the accuracy in Stage 6 is low, check the `S5_V1` files to see why the "Judge" flagged certain quotes as metaphorical errors.

---



