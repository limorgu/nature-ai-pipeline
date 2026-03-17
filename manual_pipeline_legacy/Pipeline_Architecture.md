

```
PIPELINE_ARCHITECTURE.md
```

It explains the pipeline and includes a **diagram of the full data flow centered around `MAIN_PIPELINE.py`**.

---

# 📊 Pipeline Architecture

**Book → AI Research Dataset Pipeline**

This document explains the architecture of the project and how the different pipeline stages interact.

The system converts **physical book photos** into a **structured AI-generated research dataset** through a series of modular stages orchestrated by:

```
MAIN_PIPELINE.py
```

Each stage has a specific responsibility and writes outputs to dedicated folders.

---

# 🧠 High-Level Pipeline Overview

The pipeline follows a **progressive refinement architecture**:

```
Book Photos
     ↓
OCR Digitization
     ↓
Structured Text Library
     ↓
AI Quote Extraction
     ↓
Library Audit
     ↓
Cross-Model Benchmarking
```

---

# 🏗 Full Pipeline Diagram

```
                           +-----------------------+
                           |   Feb_books_test/     |
                           |  Raw Book Photos      |
                           +-----------+-----------+
                                       |
                                       |
                                       ▼
                       +-------------------------------+
                       | Stage 2–3: OCR Librarian      |
                       | Converts images → page JSON   |
                       +---------------+---------------+
                                       |
                                       ▼
                     +--------------------------------------+
                     | Organized_Library_Source/            |
                     | Structured text per page             |
                     +----------------+---------------------+
                                      |
                                      ▼
                     +--------------------------------------+
                     | Stage 3.5 Metadata Aggregation       |
                     | Word counts / completion stats       |
                     +----------------+---------------------+
                                      |
                                      ▼
                     +--------------------------------------+
                     | Stage 4 Quote Extraction             |
                     | AI model scans pages for topic       |
                     +----------------+---------------------+
                                      |
                                      ▼
                    +---------------------------------------+
                    | Gold_Standardized/                    |
                    | topic → model → book                  |
                    | Extracted quotes dataset              |
                    +----------------+----------------------+
                                     |
                                     ▼
                    +---------------------------------------+
                    | Stage 5 Library Audit                 |
                    | Density / relevancy statistics        |
                    +----------------+----------------------+
                                     |
                                     ▼
                    +---------------------------------------+
                    | Library_Audits/                       |
                    | CSV reports and summaries             |
                    +----------------+----------------------+
                                     |
                                     ▼
                    +---------------------------------------+
                    | Stage 6 Model Comparison              |
                    | Compare extraction across models      |
                    +---------------------------------------+
```

---

# ⚙️ Pipeline Controller

All stages are executed through the **pipeline orchestrator**:

```
MAIN_PIPELINE.py
```

Running:

```bash
python MAIN_PIPELINE.py
```

opens the stage menu.

Example menu:

```
Stage 0  Library Sanitization
Stage 2–3 OCR Librarian
Stage 3.5 Metadata Aggregation
Stage 4 Quote Extraction
Stage 5 Library Audit
Stage 6 Model Comparison
Full Pipeline Run
```

---

# 🧩 Stage Responsibilities

| Stage     | Role                                    |
| --------- | --------------------------------------- |
| Stage 0   | Clean and standardize library structure |
| Stage 2–3 | OCR processing and page text extraction |
| Stage 3.5 | Metadata statistics for each book       |
| Stage 4   | AI quote extraction for selected topic  |
| Stage 5   | Audit extraction density and quality    |
| Stage 6   | Compare outputs across AI models        |

---

# 🤖 Model Routing

The pipeline supports **multiple LLM providers**.

Routing is controlled through:

```
pipeline_config.py
```

Example:

```python
CURRENT_MODEL = "gpt-4o-mini"
CURRENT_TOPIC = "nature"
```

Supported models include:

| Model          | Provider |
| -------------- | -------- |
| gpt-4o-mini    | OpenAI   |
| gpt-4o         | OpenAI   |
| deepseek-chat  | DeepSeek |
| llama3.1:8b    | Ollama   |
| deepseek-r1:8b | Ollama   |

---

# 📂 Data Organization

The project maintains **clear separation between raw data, intermediate data, and research outputs**.

```
Feb_books_test/
    Raw book images

Feb_results/
    Organized_Library_Source/
    OCR text library

Gold_Standardized/
    topic → model → book
    extracted datasets

Library_Audits/
    audit reports and CSV summaries
```

---

# 🔬 Research Capabilities

The pipeline enables:

### Literary analysis

Mapping themes across memoirs and narratives.

### Model benchmarking

Testing how different LLMs extract structured information.

### Dataset creation

Generating structured datasets from physical books.

---

# 🚀 Future Extensions

Planned improvements include:

* metaphor detection
* semantic clustering of quotes
* cross-author comparison
* taxonomy of nature imagery
* AI-assisted literary analysis



---
