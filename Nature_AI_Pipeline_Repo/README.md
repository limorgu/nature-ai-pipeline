This **Master README** is designed to be your project’s "Source of Truth." It documents the exact folder structure, the logic behind each stage, and how the data flows from a raw photo to a verified nature insight.

---

This hierarchical and "Process-Aware" architecture captures the logic of Time-Capsule** folder structure and the central orchestrator.

---

# 📚 Book-to-Nature AI Research Pipeline

This project automates the extraction of nature-related imagery and themes from physical books. It uses a **Multi-Stage AI Pipeline** to digitize, audit, and verify content with high precision while maintaining a strict, auditable data lineage.

## 📂 Master Directory Structure

The project follows a **Hierarchical Taxonomy** to ensure that research runs are isolated and deterministic.

| Folder / File | Purpose |
| --- | --- |
| `Feb_books_test/` | **The Source**: Raw `.jpg` or `.png` photos of book pages. |
| `Feb_results/Organized_Library_Source/` | **Master Library**: Ground-truth JSON text for every page. |
| `Feb_results/openai_audits/` | **Research Hub**: Organized by `[Book_Name_Timestamp]/[Stage_Version]`. |
| `Feb_results/Archives/` | **The Vault**: Timestamped archives of old or legacy runs created by Stage 0. |
| `library_final_metadata.json` | **The Handshake**: The current "Map" of the library's completion status. |

---

## ⚙️ The 7-Stage Workflow

### Stage 0: The Architect (Pre-flight)

* **Goal**: Validate source folder names (`Title_Author`) and organize the workspace.
* **Logic**: Performs an **In-Place Organization**. It moves loose files into their respective book folders and validates naming conventions to prevent pipeline breakage.

### Stage 1: Initial OCR Extraction

* **Goal**: Convert raw images into verbatim text JSON files.
* **Logic**: Duplication-aware; it skips any image already found in the Master Library to save API costs.

### Stage 2 & 3: The Librarian (Audit & Smart Fill)

* **Goal**: Ensure the digital library is a 100% complete "Twin" of the physical book.
* **Logic**: Identifies gaps in page sequences and allows for iterative, prioritized filling.

### Stage 4: Nature Extraction (The Gatherer)

* **Goal**: High-recall harvest of every potential nature mention.
* **Logic**: **Awareness-driven**; it scans existing `openai_audits` history and skips pages already harvested.
* **Output**: `.../openai_audits/[Book_Name_Timestamp]/S4_V1/`.

### Stage 5: Wise Audit (The Judge)

* **Goal**: Precision filtering to remove metaphorical "False Positives" (e.g., "lion-hearted").
* **Logic**: A high-reasoning model (GPT-4o) audits Stage 4 drafts and categorizes verified quotes.
* **Output**: `.../openai_audits/[Book_Name_Timestamp]/S5_V1/`.

### Stage 6: Gold Standard & Performance

* **Goal**: Consolidate "Clean" data and generate accuracy reports.
* **Logic**: Purifies the dataset into a final JSON and generates a global CSV report.
* **Output**: `.../openai_audits/[Book_Name_Timestamp]/S6_Gold/`.

---

## 🚀 Quickstart: Running the Orchestrator

Run the central menu to manage the entire lifecycle:

```bash
python main.py

```

### **1. To Digitize & Build the Library (Process A)**

Select **Option [1]**. This runs Stages 1-3 to ensure your source text is 100% complete before you start thematic research.

### **2. To Run Research (Process B - Stage 4 and after)**

Select **Option [2]**. This is your "Daily Driver" for analysis. It handles:

1. **Extraction**: Pulls new nature quotes from the library.
2. **Verification**: Audits them for metaphorical errors.
3. **Purification**: Creates your "Gold Standard" dataset.

### **3. To Clean the Workspace**

Select **Option [0]**. Use this if your `openai_audits` folder feels cluttered; it will sort loose files into their proper hierarchical homes.

---

## 🛡 Safeguards & Principles

* **Deterministic Lineage**: Every file is saved within a timestamped "Time-Capsule" folder, ensuring you can trace any "Gold" quote back to its raw extraction.
* **Methodological Containment**: By separating **Extraction** from **Verification**, you contain AI hallucinations within a single, fixable module.
* **State-Awareness**: The pipeline "remembers" what it has already done, preventing redundant API charges.


