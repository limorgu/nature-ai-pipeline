






---

## ⚡ Quickstart: Launching the Lab

Follow these steps to initialize your research environment and run your first extraction.

### 1. Environment Setup

Clone the repository and install the necessary dependencies.

```bash
# 1. Clone the lab
git clone https://github.com/YOUR_USERNAME/AI-Research-Engine.git
cd AI-Research-Engine

# 2. Set up your virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

```

### 2. Configure Your "Global Brain"

Open `pipeline_config.py` to set your research target. This centralizes your variables so you don't have to hunt through stage files.

```python
# pipeline_config.py
CURRENT_TOPIC = "nature"      # The theme you are extracting
CURRENT_MODEL = "gpt-4o-mini" # Options: gpt-4o, deepseek-chat, llama3.1:8b

```

### 3. Initialize the Library

If you are starting fresh, run the setup script to create the necessary directory tree:

```bash
python3 setup_library.py

```

### 4. Run the Orchestrator

Launch the main menu to execute stages individually or run the full automation.

```bash
python MAIN_PIPELINE.py

```

> **Pro Tip:** For a first run, use **Option [0]** to sanitize your filenames, then **Option [1]** to trigger the Librarian OCR. Once your `Organized_Library_Source` is populated, use **Option [A]** for a full automated sweep.





---



