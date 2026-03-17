
---

# 🚀 QuickStart Guide

**Book → AI Research Dataset Pipeline**

This guide explains how to process a book from **raw photos** into an **AI-extracted research dataset** using the project pipeline.

The entire system is orchestrated through:

```
MAIN_PIPELINE.py
```

---

# 🛠 Prerequisites

### 1️⃣ Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Set API keys (for cloud models)

If using OpenAI models:

```bash
export OPENAI_API_KEY="your_key_here"
```

Optional (DeepSeek API):

```bash
export DEEPSEEK_API_KEY="your_key_here"
```

---

### 3️⃣ Optional: install local models (Ollama)

This lets you run models **without API cost**.

Install Ollama:

[https://ollama.com](https://ollama.com)

Pull a model:

```bash
ollama pull llama3.1:8b
```

or

```bash
ollama pull deepseek-r1:8b
```

---

# 📂 Step 0 — Add Book Photos

Place images inside:

```
Feb_books_test/
```

Each book must have its own folder:

```
Feb_books_test/
    Educated_TaraWestover/
    TheGlassCastle_JeannetteWalls/
```

Naming format:

```
Title_Author
```

Example:

```
Educated_TaraWestover
```

---

# ⚙️ Step 1 — Configure Model & Topic

Open:

```
pipeline_config.py
```

Choose the **model** and **topic**.

Example:

```python
CURRENT_MODEL = "gpt-4o-mini"
CURRENT_TOPIC = "nature"
```

Supported models include:

```
gpt-4o-mini
gpt-4o
deepseek-chat
llama3.1:8b
deepseek-r1:8b
```

---

# ▶️ Step 2 — Launch the Pipeline

Run the orchestrator:

```bash
python MAIN_PIPELINE.py
```

You will see the **Pipeline Menu**.

Example structure:

```
Stage 0  Library Sanitization
Stage 2–3  OCR Librarian
Stage 3.5  Metadata Aggregation
Stage 4  Quote Extraction
Stage 5  Library Audit
Stage 6  Model Comparison
Full Pipeline Run
```

---

# 📸 Stage 2–3 — OCR Librarian

Goal: Convert images into structured text.

This stage:

1. scans the book folder
2. identifies missing pages
3. processes images using OCR
4. saves text as JSON

Output location:

```
Feb_results/Organized_Library_Source/
```

Each page becomes:

```
page_001.json
page_002.json
```

Goal: **100% completion for each book**.

---

# 📊 Stage 3.5 — Metadata Aggregation

This stage calculates statistics such as:

* total word count
* page counts
* completion status

Saved in:

```
folder_metadata.json
```

---

# 🌿 Stage 4 — Quote Extraction

This is the **core AI stage**.

The model scans page text and extracts quotes related to the selected topic.

Example topic:

```
nature
```

Example extracted item:

```json
{
 "quote": "The mountains glowed under the snow.",
 "relevancy": 2,
 "page_id": "page_014"
}
```

Results are stored by:

```
topic → model → book
```

Example:

```
Gold_Standardized/
    nature/
        gpt-4o-mini/
            Educated/
```

---

# 🔍 Stage 5 — Library Audit

Analyzes extraction results across books.

Metrics include:

* quotes per book
* average relevancy
* extraction density

Output folder:

```
Library_Audits/
```

Example files:

```
summary.csv
density_report.csv
```

---

# 🤖 Stage 6 — Model Comparison

Compare how different models perform on the same dataset.

Example:

| Model         | Quotes Found |
| ------------- | ------------ |
| gpt-4o-mini   | 512          |
| deepseek-chat | 463          |
| llama3.1:8b   | 389          |

Useful for benchmarking model extraction quality.

---

# 🧪 Recommended First Run

1️⃣ Configure model

```
CURRENT_MODEL = "gpt-4o-mini"
```

2️⃣ Run pipeline

```bash
python MAIN_PIPELINE.py
```

3️⃣ Execute stages in order:

```
Stage 2–3 → OCR
Stage 3.5 → Metadata
Stage 4 → Extraction
Stage 5 → Audit
```

---

# 📂 Where Your Files Are Stored

### OCR text

```
Feb_results/Organized_Library_Source/
```

---

### Extracted quotes

```
Gold_Standardized/
    [topic]/
        [model]/
            [book]/
```

---

### Audit reports

```
Library_Audits/
```

---

# 🆘 Troubleshooting

### Book not detected

Ensure the folder name follows:

```
Title_Author
```

Example:

```
Educated_TaraWestover
```

---

### Extraction returns empty results

Check:

* OCR pages contain text
* model is available
* topic is correct

Example working configuration:

```python
CURRENT_MODEL = "llama3.1:8b"
```

---

### Local model not responding

Ensure Ollama is running:

```bash
ollama serve
```

Test the model:

```bash
ollama run llama3.1:8b
```

---

If you'd like, I can also help you create **one more file that will dramatically improve the repo**:

```
PIPELINE_ARCHITECTURE.md
```


