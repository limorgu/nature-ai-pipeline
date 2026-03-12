

---


* `pipeline_config.py` controls **model + topic**
* stages run through **`main.py` menu**
* **model-specific results are separated automatically**
* works with **OpenAI / DeepSeek / Ollama local models**
* no hard dependency on Worker/Judge models anymore
* extraction produces **per-model gold datasets**
* Stage 6 compares models

Below is a **clean updated README that matches your current system**.

---

# 📚 AI Book Research Pipeline

**Updated Architecture – Model-Agnostic Pipeline**

This project builds a **structured research dataset from physical books** using a **multi-stage AI pipeline**.
It converts photographed pages into machine-readable text and extracts thematic quotes using configurable AI models.

The pipeline is designed to:

* support **multiple LLM providers** (OpenAI, DeepSeek, Ollama)
* keep **model outputs isolated for benchmarking**
* produce **clean research datasets for downstream analysis**

---

# 🧠 Pipeline Design Philosophy

The system separates responsibilities into clear stages:

| Stage        | Responsibility                   |
| ------------ | -------------------------------- |
| Digitization | Convert photos → structured text |
| Extraction   | Detect thematic quotes           |
| Audit        | Evaluate extraction density      |
| Comparison   | Compare model outputs            |

All model behavior is controlled centrally through:

```
pipeline_config.py
```

Changing a single variable can redirect the entire pipeline to a different model.

---

# 📂 Directory Structure

```
data_test/
│
├── Feb_books_test/
│   Raw photographed book pages
│
├── Feb_results/
│   Intermediate OCR results
│
│   └── Organized_Library_Source/
│       Structured page JSON for each book
│
├── Gold_Standardized/
│   Model-specific extracted datasets
│
│   └── [topic]/
│        └── [model]/
│            └── [book]/
│                 final extraction JSON
│
├── Library_Audits/
│   Model density reports and CSV summaries
│
└── library_final_metadata.json
    Library completion and OCR progress tracking
```

---

# ⚙️ Global Configuration

All pipeline settings live in:

```
pipeline_config.py
```

Main parameters:

```python
CURRENT_MODEL = "gpt-4o-mini"
CURRENT_TOPIC = "nature"
```

Examples:

```
gpt-4o-mini
gpt-4o
deepseek-chat
llama3.1:8b
deepseek-r1:8b
```

This allows testing **different models on the same dataset**.

---

# 🔬 Multi-Stage Workflow

## Stage 0 — Library Sanitization

**Purpose**

Prepare the dataset and ensure all folders and filenames are consistent.

**Output**

Clean source image library ready for OCR.

---

# Stage 2-3 — OCR Librarian

**Goal**

Convert photographed pages into structured text.

**Process**

1. Detect missing pages
2. OCR missing images
3. Save structured page JSON

Each page becomes:

```
page_001.json
page_002.json
...
```

Stored in:

```
Organized_Library_Source/[BookName]/
```

Example page JSON:

```json
{
 "page_id": "page_001",
 "content": "The forest smelled of wet earth and pine..."
}
```

---

# Stage 3.5 — Metadata Aggregation

**Goal**

Calculate basic statistics for each book.

Metrics include:

* total word count
* pages processed
* OCR completion status

Saved in:

```
folder_metadata.json
```

Example:

```json
{
 "book": "Educated",
 "total_word_count": 102341
}
```

---

# Stage 4 — Quote Extraction (Core AI Stage)

**Goal**

Extract thematic quotes from each page.

The system scans page text and asks an AI model to detect quotes relevant to a selected **topic**.

Example topic:

```
nature
```

Prompt behavior:

```
Analyze text and detect quotes related to nature.
Return JSON with:
quote
relevancy score
page id
```

Example model output:

```json
{
 "found": true,
 "items": [
  {
   "quote": "The mountains glowed under the first snow.",
   "relevancy": 2
  }
 ]
}
```

---

## Model Support

Stage 4 automatically routes requests based on model name.

| Model Type    | Routing             |
| ------------- | ------------------- |
| OpenAI        | OpenAI Cloud API    |
| DeepSeek      | DeepSeek API        |
| Ollama models | Local Ollama server |

Examples:

```
gpt-4o-mini
deepseek-chat
llama3.1:8b
deepseek-r1:8b
```

No code change required — only update:

```
CURRENT_MODEL
```

---

# Stage 5 — Library Audit

**Goal**

Analyze extraction quality and density.

Metrics include:

* quotes per book
* average relevancy
* extraction density

Results saved as:

```
Library_Audits/Audit_[topic]_[timestamp]
```

Example outputs:

```
summary.csv
density_report.csv
```

---

# Stage 6 — Model Comparison

**Goal**

Compare extraction behavior between models.

Example experiment:

| Model         | Quotes Found |
| ------------- | ------------ |
| gpt-4o-mini   | 512          |
| deepseek-chat | 463          |
| llama3.1:8b   | 389          |

This allows benchmarking:

* model sensitivity
* topic detection accuracy
* extraction density

---

# 🚀 Running the Pipeline

The system is controlled through the **Research Orchestrator**:

```
main.py
```

Run:

```
python main.py
```

Menu:

```
[0] Stage 0  Sanitization
[1] Stage 2-3 OCR Librarian
[2] Stage 3.5 Metadata Aggregation
[3] Stage 4 Extraction
[4] Stage 5 Audit
[5] Stage 6 Model Comparison
[A] Full pipeline run
```

---

# 🧪 Example Experiment Workflow

Example experiment:

```
Topic: nature
```

Run pipeline with:

```
gpt-4o-mini
deepseek-chat
llama3.1:8b
```

Each model produces its own dataset:

```
Gold_Standardized/
   nature/
      gpt-4o-mini/
      deepseek-chat/
      llama3.1:8b/
```

This allows **clean cross-model comparison**.

---

# 🧬 Research Use Cases

This pipeline enables:

### Literary analysis

Mapping nature imagery across memoirs.

### Model benchmarking

Testing LLM extraction capabilities.

### Dataset creation

Building structured quote datasets for:

* NLP research
* literary analysis
* AI benchmarking

```
See PIPELINE_ARCHITECTURE.md for a visual overview of the pipeline: Pipeline_Architecture.md
```

---




---

