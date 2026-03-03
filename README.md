

---

# 📚 Generic-to-Insight: The Multi-Stage AI Research Pipeline

This project provides a robust, reproducible framework for turning raw physical media (photos of books/documents) into verified, structured datasets. While this specific instance is configured for **Nature Extraction**, the modular architecture is designed to be adapted for any thematic analysis (e.g., medical, legal, historical, or emotional sentiment).

## 📂 Master Directory Structure

The hierarchy is strictly organized to maintain **Data Lineage**—ensuring the "Raw" never mixes with the "Processed."

| Folder / File | Purpose |
| --- | --- |
| `Source_Data/` | **The Input:** Raw `.jpg` or `.png` photos of source material. |
| `Organized_Library/` | **The Master Library:** Verbatim JSON text digitized from images. |
| `Thematic_Drafts/` | **The Gatherer Output:** Potential thematic quotes (High Recall). |
| `Final_Audits/` | **The Gold Standard:** Verified and categorized insights (High Precision). |
| `Library_Audits/` | **Tracking:** Logs of completion stats and data word counts. |
| `final_metadata.json` | **The Handshake:** The dynamic "Map" of the library's progress. |

---

## ⚙️ The 6-Stage Workflow (Thematic-Agnostic)

### Stage 1-3: The Digitization Engine

* **Goal:** Create a 1:1 digital twin of the physical source.
* **Logic:** Uses Vision AI for OCR. It is **duplication-aware** and uses a **Priority Queue** system to identify gaps (missing pages) and fill them iteratively.
* **Key Learning:** You cannot analyze what you haven't accurately digitized.

### Stage 4: The Gatherer (High Recall)

* **Goal:** Scour the digital library for potential thematic matches.
* **Model:** Optimized for speed and breadth (e.g., `gpt-4o-mini`).
* **Customization:** Simply swap the "Nature" prompt for any other theme (e.g., "Find all mentions of medical symptoms" or "Identify legal obligations").

### Stage 5: The Judge (High Precision)

* **Goal:** Verify the Gatherer’s work and remove "False Positives" (like metaphors or contextually irrelevant matches).
* **Model:** High-reasoning (e.g., `gpt-4o`).
* **Logic:** This stage acts as a "Wise Auditor" to ensure data integrity before final analysis.

### Stage 6: The Accuracy Dashboard

* **Goal:** Quantify the reliability of the AI extraction.
* **Output:** A CSV report comparing the AI's results against ground truth, allowing for iterative prompt engineering.

---

## 🚀 The Operational Loop

1. **Digitize:** Run the **Master Runner (Stage 2 + 3)** to build your digital library.
2. **Extract:** Run **Stage 4** using your specific thematic criteria.
3. **Verify:** Run **Stage 5** to refine the raw extractions into high-quality data.
4. **Report:** Run **Stage 6** to see the error rates and improve the pipeline.

---

## 🛡 Architectural Safeguards

* **Immutability:** The Master Library is "Append Only." The pipeline never deletes original digitized text.
* **Modular Separation:** Every stage has its own output folder. This prevents **Recursive Bias** (where an AI error in Stage 4 is treated as a fact in Stage 5).
* **State Verification:** Stage 0 scripts verify folder naming and pathing before a single dollar is spent on API calls.

---

